# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import UserError

from odoo import models, _

_logger = logging.getLogger(__name__)


class TaxReport(models.AbstractModel):
    _name = "report.atw_tax_reports.tax_report.xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):

        tax_report_invoice_domain = [
            ('date', '>=', data['start_date']),
            ('date', '<=', data['end_date']),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
        ]
        tax_report_bill_domain = [
            ('date', '>=', data['start_date']),
            ('date', '<=', data['end_date']),
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('state', '=', 'posted'),
        ]

        tax_report_invoices = self.env['account.move'].search(
            tax_report_invoice_domain,
            order="invoice_date"
        )

        # Filter out the zero tax invoices
        zero_tax_invoices = self.env['account.move'].browse()
        for inv in tax_report_invoices:
            for line in inv.invoice_line_ids:
                if not line.tax_ids:
                    zero_tax_invoices += inv
                else:
                    for tax in line.tax_ids:
                        if '0' in tax.name or 'Exempted' in tax.name:
                            if not inv in zero_tax_invoices:
                                zero_tax_invoices += inv
        if zero_tax_invoices:
            tax_report_invoices -= zero_tax_invoices

        # Get pos orders with tax
        pos_orders = self.env['pos.order'].search([
            ('state', 'in', ['done', 'invoiced']),
            ('amount_tax', '>', 0),
            ('date_order', '>=', data['start_date']),
            ('date_order', '<=', data['end_date']),
        ])

        other_entries_with_tax = self.env['account.move'].search([
            ('date', '>=', data['start_date']),
            ('date', '<=', data['end_date']),
            ('move_type', '=', 'entry'),
            ('state', '=', 'posted'),
        ])

        # Get the other journal entries with 5% sales type tax
        fiveper_tax_entries = self.env['account.move'].browse()
        for move in other_entries_with_tax:
            for line in move.line_ids:
                if line.tax_line_id and line.tax_line_id.type_tax_use == 'sale':
                    if '5' in line.tax_line_id.name:
                        if not move in fiveper_tax_entries:
                            fiveper_tax_entries += move

        tax_report_bills = self.env['account.move'].search(
            tax_report_bill_domain,
            order="invoice_date"
        )

        # Get the other journal entries with 5% purchase type tax
        fiveper_purchase_tax_entries = self.env['account.move'].browse()
        for move in other_entries_with_tax:
            for line in move.line_ids:
                if line.tax_line_id and line.tax_line_id.type_tax_use == 'purchase':
                    if '5' in line.tax_line_id.name:
                        if not move in fiveper_purchase_tax_entries:
                            fiveper_purchase_tax_entries += move

        _logger.info(
            '''
            ----------------------{ Wizard Date Range }--------------------------------
            From: %s - To: %s
            ----------------------{ Tax Reportable Invoices }-------------------------------
            %s
            ----------------------{ Zero Tax Invoices }-------------------------------
            %s
            ----------------------{ Tax Reportable Bills }-------------------------------
            %s
            ----------------------{ POS Orders }-------------------------------
            %s
            ----------------------{ Other entries related to sales tax }-----------------------
            %s
            ----------------------{ Other entries related to purchase tax }-----------------------
            %s
            
            ''' % (
                data['start_date'],
                data['end_date'],
                len(tax_report_invoices),
                len(zero_tax_invoices),
                len(tax_report_bills),
                len(pos_orders),
                len(fiveper_tax_entries),
                len(fiveper_purchase_tax_entries)
            )
        )

        if not tax_report_invoices \
            and not tax_report_bills\
                and not pos_orders \
        and not fiveper_tax_entries\
                and not fiveper_purchase_tax_entries:
            raise UserError("No Data found for Tax Report.")

        invoice_tax_report_sheet = workbook.add_worksheet(
            "Std Rated Sales - Box 1(a)")
        bill_tax_report_sheet = workbook.add_worksheet(
            "Input Tax - Box 6(a)")
        self.print_invoice_header(workbook, invoice_tax_report_sheet)
        self.print_invoice_data(
            data, workbook,
            invoice_tax_report_sheet,
            tax_report_invoices,
            pos_orders,
            fiveper_tax_entries
        )
        self.print_bill_header(workbook, bill_tax_report_sheet)
        self.print_bill_data(
            data, workbook,
            bill_tax_report_sheet,
            tax_report_bills,
            fiveper_purchase_tax_entries
        )

        # Manual adjustment of the columns width
        invoice_tax_report_sheet.set_column(0, 25, 25)
        bill_tax_report_sheet.set_column(0, 25, 25)

    def print_invoice_header(self, workbook, sheet):
        format_header = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "center",
                "bold": True,
                "font_color": "#843C0B",
                "bg_color": "#D9D9D9",
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_header_no_bg_left = workbook.add_format(
            {"font_name": "Arial", "font_size": 12,
                "align": "left", "bold": True}
        )

        # Title
        sheet.merge_range(
            'A1:K1',
            'Supplies of goods / services taxed at 5% - Box 1(a)* - If Group Should be Split By Group Member',
            format_header_no_bg_left
        )

        # Columns
        sheet.write("A3", "Serial #", format_header)
        sheet.write("B3", "Taxpayer VATIN", format_header)
        sheet.write(
            "C3",
            "Taxpayer Name / Member Company Name (If applicable)",
            format_header
        )
        sheet.write("D3", "Tax Invoice/Tax Credit Note #", format_header)
        sheet.write(
            "E3", "Tax Invoice/Tax credit note Date - DD/MM/YYYY format only", format_header)
        sheet.write(
            "F3", "Reporting period (From DD/MM/YYYY to DD/MM/YYYY format only)", format_header)
        sheet.write(
            "G3", " Tax Invoice/Tax credit note Amount OMR (before VAT) ", format_header)
        sheet.write(
            "H3", "Vat Amount OMR", format_header)
        sheet.write(
            "I3", "Customer Name", format_header)
        sheet.write(
            "J3", "Customer VATIN", format_header)
        sheet.write(
            "K3", "Clear description of the supply", format_header)

    def print_invoice_data(self, data, workbook, sheet, invoice_data, pos_data, entry_data):
        format_numeric = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": False,
                "num_format": "#,##0.000",
                "font_color": "black",
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_numeric_bold = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": True,
                "num_format": "#,##0.000",
                "font_color": "black",
            }
        )
        format_string_left = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "left",
                "bold": False,
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_string_yellow = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "left",
                "bold": True,
                "bg_color": "FFFF00"
            }
        )
        format_string_bold = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": True,
            }
        )
        format_string_center = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "center",
                "bold": False,
                "border": 1,
                "border_color": "#000000",
            }
        )

        row = 3
        total_untaxed = total_tax = 0
        data_index = 0
        for idx, invoice in enumerate(invoice_data):
            invoice_date = invoice.invoice_date.strftime('%d/%m/%Y')
            if invoice.move_type == 'out_invoice':
                total_untaxed += invoice.amount_untaxed
                total_tax += invoice.amount_tax
            else:
                total_untaxed -= invoice.amount_untaxed
                total_tax -= invoice.amount_tax

            sheet.write(row, 0, idx+1, format_string_left)
            sheet.write(row, 1, data['vatin'], format_string_left)
            sheet.write(row, 2, data['company'], format_string_left)
            sheet.write(row, 3, invoice.name, format_string_left)
            sheet.write(row, 4, invoice_date, format_string_left)
            sheet.write(row, 5, "From %s to %s" % (
                data['formatted_start_date'],
                data['formatted_end_date']
            ),
                format_string_left
            )
            sheet.write(row, 6, invoice.amount_untaxed, format_numeric)
            sheet.write(row, 7, invoice.amount_tax, format_numeric)
            sheet.write(row, 8, invoice.partner_id.name, format_string_left)
            sheet.write(row, 9, invoice.partner_id.vat or '',
                        format_string_left)
            sheet.write(row, 10, '-', format_string_center)

            row += 1
            data_index = idx

        # Pos orders
        for pos in pos_data:
            pos_date = pos.date_order.strftime('%d/%m/%Y')
            amount_untaxed = pos.amount_total - pos.amount_tax
            total_untaxed += amount_untaxed
            total_tax += pos.amount_tax
            data_index += 1

            sheet.write(row, 0, data_index+1, format_string_left)
            sheet.write(row, 1, data['vatin'], format_string_left)
            sheet.write(row, 2, data['company'], format_string_left)
            sheet.write(row, 3, pos.name, format_string_left)
            sheet.write(row, 4, pos_date, format_string_left)
            sheet.write(row, 5, "From %s to %s" % (
                data['formatted_start_date'],
                data['formatted_end_date']
            ),
                format_string_left
            )
            sheet.write(row, 6, amount_untaxed, format_numeric)
            sheet.write(row, 7, pos.amount_tax, format_numeric)
            sheet.write(row, 8, pos.partner_id.name, format_string_left)
            sheet.write(row, 9, pos.partner_id.vat or '',
                        format_string_left)
            sheet.write(row, 10, '-', format_string_center)

            row += 1

        # 5% tax journal entries
        for move in entry_data:
            move_date = move.date.strftime('%d/%m/%Y')
            move_tax = move_amount_untaxed = 0.0
            data_index += 1

            sheet.write(row, 0, data_index+1, format_string_left)
            sheet.write(row, 1, data['vatin'], format_string_left)
            sheet.write(row, 2, data['company'], format_string_left)
            sheet.write(row, 3, move.name, format_string_left)
            sheet.write(row, 4, move_date, format_string_left)
            sheet.write(row, 5, "From %s to %s" % (
                data['formatted_start_date'],
                data['formatted_end_date']
            ),
                format_string_left
            )

            # Get total tax amount and untax amount
            tax_lines = move.line_ids.filtered(
                lambda line: line.name and 'VAT 5' in line.name
            )
            move_tax += sum(tax_lines.mapped('credit'))
            move_amount_untaxed = move.amount_total - move_tax
            total_untaxed += move_amount_untaxed
            total_tax += move_tax

            sheet.write(row, 6, move_amount_untaxed, format_numeric)
            sheet.write(row, 7, move_tax, format_numeric)
            sheet.write(row, 8, move.partner_id.name or '', format_string_left)
            sheet.write(row, 9, move.partner_id.vat or '',
                        format_string_left)
            sheet.write(row, 10, '-', format_string_center)

            row += 1

        sheet.merge_range(
            'A%s:E%s' % (row+1, row+1),
            "*Total value of standard rated supplies of goods and services in the Sultanate, including deemed supplies.",
            format_string_yellow
        )

        row += 1
        sheet.write(
            row,
            5,
            "Total",
            format_string_bold
        )
        sheet.write(
            row,
            6,
            total_untaxed,
            format_numeric_bold
        )
        sheet.write(
            row,
            7,
            total_tax,
            format_numeric_bold
        )
        # Get total untax amount and tax amount

    def print_bill_header(self, workbook, sheet):
        format_header = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "center",
                "bold": True,
                "font_color": "#843C0B",
                "bg_color": "#D9D9D9",
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_header_no_bg_left = workbook.add_format(
            {"font_name": "Arial", "font_size": 12,
                "align": "left", "bold": True}
        )

        # Title
        sheet.merge_range(
            'A1:M1',
            "Purchases (except import of goods) - BOX 6(a)* - If Group Should be Split By Group Member",
            format_header_no_bg_left
        )

        # Columns
        sheet.write("A3", "Serial #", format_header)
        sheet.write("B3", "Taxpayer VATIN", format_header)
        sheet.write(
            "C3",
            "Taxpayer Name / Member Company Name (If applicable)",
            format_header
        )
        sheet.write("D3", "Tax Invoice/Tax Credit Note #", format_header)
        sheet.write(
            "E3", "Tax Invoice/Tax credit note Date - DD/MM/YYYY format only", format_header)
        sheet.write(
            "F3", "Tax Invoice/Tax credit note Received Date - DD/MM/YYYY format only", format_header)
        sheet.write(
            "G3", "Reporting period (From DD/MM/YYYY to DD/MM/YYYY format only)", format_header)
        sheet.write(
            "H3", " Tax Invoice/Tax credit note Amount OMR (before VAT) ", format_header)
        sheet.write(
            "I3", "Vat Amount OMR", format_header)
        sheet.write(
            "J3", "Vat Amount Claimed OMR", format_header)
        sheet.write(
            "K3", "Supplier Name", format_header)
        sheet.write(
            "L3", "Supplier VATIN", format_header)
        sheet.write(
            "M3", "Clear description of the supply", format_header)

    def print_bill_data(
            self, data, workbook,
            sheet,
            invoice_data,
            entry_data):
        format_numeric = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": False,
                "num_format": "#,##0.000",
                "font_color": "black",
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_numeric_bold = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": True,
                "num_format": "#,##0.000",
                "font_color": "black",
            }
        )
        format_string_left = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "left",
                "bold": False,
                "border": 1,
                "border_color": "#000000",
            }
        )
        format_string_yellow = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "left",
                "bold": True,
                "bg_color": "FFFF00"
            }
        )
        format_string_bold = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "right",
                "bold": True,
            }
        )
        format_string_center = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 11,
                "align": "center",
                "bold": False,
                "border": 1,
                "border_color": "#000000",
            }
        )

        row = 3
        data_index = 0
        total_untaxed = total_tax = 0
        for idx, invoice in enumerate(invoice_data):
            invoice_date = invoice.invoice_date.strftime('%d/%m/%Y')
            if invoice.move_type == 'in_invoice':
                total_untaxed += invoice.amount_untaxed
                total_tax += invoice.amount_tax
            else:
                total_untaxed -= invoice.amount_untaxed
                total_tax -= invoice.amount_tax

            sheet.write(row, 0, idx+1, format_string_left)
            sheet.write(row, 1, data['vatin'], format_string_left)
            sheet.write(row, 2, data['company'], format_string_left)
            sheet.write(row, 3, invoice.name, format_string_left)
            sheet.write(row, 4, invoice_date, format_string_left)
            sheet.write(row, 5, "-", format_string_left)    # Received Date?
            sheet.write(row, 6, "From %s to %s" % (
                data['formatted_start_date'],
                data['formatted_end_date']
            ),
                format_string_left
            )
            sheet.write(row, 7, invoice.amount_untaxed, format_numeric)
            sheet.write(row, 8, invoice.amount_tax, format_numeric)
            sheet.write(row, 9, invoice.amount_untaxed +
                        invoice.amount_tax, format_numeric)  # Vat amount claimed
            sheet.write(row, 10, invoice.partner_id.name, format_string_left)
            sheet.write(row, 11, invoice.partner_id.vat or '',
                        format_string_left)
            sheet.write(row, 12, '-', format_string_center)
            row += 1
            data_index = idx

        # 5% tax journal entries
        for move in entry_data:
            move_date = move.date.strftime('%d/%m/%Y')
            move_tax = move_amount_untaxed = 0.0
            data_index += 1

            sheet.write(row, 0, data_index+1, format_string_left)
            sheet.write(row, 1, data['vatin'], format_string_left)
            sheet.write(row, 2, data['company'], format_string_left)
            sheet.write(row, 3, move.name, format_string_left)
            sheet.write(row, 4, move_date, format_string_left)
            sheet.write(row, 5, "-", format_string_left)    # Received Date?
            sheet.write(row, 6, "From %s to %s" % (
                data['formatted_start_date'],
                data['formatted_end_date']
            ),
                format_string_left
            )

            # Get total tax amount and untax amount
            tax_lines = move.line_ids.filtered(
                lambda line: line.name and 'VAT 5' in line.name
            )
            move_tax += sum(tax_lines.mapped('debit'))
            move_amount_untaxed = move.amount_total - move_tax
            total_untaxed += move_amount_untaxed
            total_tax += move_tax

            sheet.write(row, 7, move_amount_untaxed, format_numeric)
            sheet.write(row, 8, move_tax, format_numeric)
            sheet.write(row, 9, move_amount_untaxed + move_tax,
                        format_numeric)  # Vat amount claimed
            sheet.write(row, 10, move.partner_id.name or '',
                        format_string_left)
            sheet.write(row, 11, move.partner_id.vat or '',
                        format_string_left)
            sheet.write(row, 12, '-', format_string_center)

            row += 1

        sheet.write(
            row,
            6,
            "Total",
            format_string_bold
        )
        sheet.write(
            row,
            7,
            total_untaxed,
            format_numeric_bold
        )
        sheet.write(
            row,
            8,
            total_tax,
            format_numeric_bold
        )
        sheet.write(    # Total vat claimed
            row,
            9,
            0,
            format_numeric_bold
        )
        row += 1

        sheet.merge_range(
            'G%s:H%s' % (row+1, row+1),
            "Deductible Reverse Charge from Box 2(b)",
            format_numeric_bold
        )

        sheet.write(    # Value for: Deductible Reverse Charge from Box 2(b)
            row,
            9,
            0,
            format_numeric_bold
        )

        row += 1

        sheet.write(
            row,
            6,
            "Total Input VAT Credit",
            format_string_bold
        )

        sheet.write(    # Value for: Total Input VAT Credit
            row,
            9,
            0,
            format_numeric_bold
        )

        row += 1

        sheet.merge_range(
            'A%s:M%s' % (row+1, row+1),
            "*Total value of all purchases including exempt/standard/zero rated purchases and reverse charge purchases. Excludes imported goods, out of scope expenses and purchases of fixed (capital) assets.",
            format_string_yellow
        )
