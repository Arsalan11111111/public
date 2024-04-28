# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)


class VatReturn(models.TransientModel):
    _name = "wizard.vat.return"
    _description = "Wizard: VAT Return Content"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    start_date = fields.Date(
        string="From",
        required=True,
        default=lambda self: fields.Date.to_string(
            datetime.date.today().replace(day=1)
        ),
    )
    end_date = fields.Date(
        string="To",
        required=True,
        default=lambda self: fields.Date.to_string((
            datetime.datetime.now() + relativedelta(months=+1, day=1, days=-1)
        ).date()),
    )

    def get_vat_return_data(self):
        AccountMove = self.env['account.move']

        invoices = AccountMove.search([
            ('move_type', '=', 'out_invoice'),
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('state', '=', 'posted')
        ])
        bills = AccountMove.search([
            ('move_type', '=', 'in_invoice'),
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('state', '=', 'posted')
        ])

        invoice_lines_with_tax = invoices.mapped('invoice_line_ids').filtered(
            lambda line: line.tax_ids
        )

        inv_five_per_taxable = inv_five_per_tax = 0.0
        inv_zero_per_taxable = 0.0
        inv_exempt_taxable = 0.0

        move_lines = self.env['account.move.line'].search([
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('parent_state', '=', 'posted')

        ])
        fiveper_tax_movelines = move_lines.filtered(
            lambda line: line.tax_line_id and line.tax_line_id.amount == 5
        )
        fiveper_sales_tax_movelines = fiveper_tax_movelines.filtered(
            lambda line: line.tax_line_id.type_tax_use == 'sale'
        )

        inv_five_per_tax = abs(
            sum(fiveper_sales_tax_movelines.mapped('balance')))

        # Get sale type taxable base
        for line in move_lines.filtered(lambda line: line.tax_ids):
            for tax in line.tax_ids[0]:
                if tax.amount == 5 and tax.type_tax_use == 'sale':
                    inv_five_per_taxable += line.balance

        for line in invoice_lines_with_tax:
            price_tax = line.price_total - line.price_subtotal
            for tax in line.tax_ids:
                if 'Exempted' in tax.name:
                    inv_exempt_taxable += line.price_subtotal
                elif '0' in tax.name:
                    inv_zero_per_taxable += line.price_subtotal

        _logger.info(
            '''
            
            -=-=-=-=-=-=-<< 5 Percent Tax and Taxable After processing invoices >>-=-=-=-=-
            Taxable: %s
            Tax: %s
            
            ''' % (inv_five_per_taxable, inv_five_per_tax)
        )

        total_vat_due = inv_five_per_tax
        bill_lines_with_tax = bills.mapped('invoice_line_ids').filtered(
            lambda line: line.tax_ids
        )
        bill_five_per_taxable = bill_five_per_tax = 0.0
        bill_import_taxable = bill_import_tax = 0.0
        bill_fix_asset_tax = 0.0
        fiveper_bills = self.env['account.move']

        fiveper_purchase_tax_lines = fiveper_tax_movelines.filtered(
            lambda line: line.tax_line_id.type_tax_use == 'purchase'
        )
        bill_five_per_tax = abs(
            sum(fiveper_purchase_tax_lines.mapped('balance')))

        # Get sale type taxable base
        for line in move_lines.filtered(lambda line: line.tax_ids):
            for tax in line.tax_ids[0]:
                if tax.amount == 5 and tax.type_tax_use == 'purchase':
                    bill_five_per_taxable += line.balance

        for line in bill_lines_with_tax:
            price_tax = line.price_total - line.price_subtotal
            for tax in line.tax_ids:
                if 'Import' in tax.name:
                    bill_import_taxable += line.price_subtotal
                    bill_import_tax += price_tax
                elif 'Fixed' in tax.name:
                    bill_fix_asset_tax += price_tax

        _logger.info(
            '''
            
            -=-=-=-=-=-=-<< 5 Percent Tax and Taxable After processing Bills >>-=-=-=-=-
            Taxable: %s
            Tax: %s
            
            ''' % (
                bill_five_per_taxable,
                bill_five_per_tax
            )
        )

        total_input_vat_credit = bill_five_per_tax + \
            bill_import_tax + bill_fix_asset_tax
        tax_liability = total_vat_due - total_input_vat_credit

        # Pack report data
        report_data = {
            'inv_five_per_taxable': abs(inv_five_per_taxable),
            'inv_five_per_tax': inv_five_per_tax,
            'inv_zero_per_taxable': inv_zero_per_taxable,
            'inv_exempt_taxable': inv_exempt_taxable,
            'bill_five_per_taxable': abs(bill_five_per_taxable),
            'bill_five_per_tax': bill_five_per_tax,
            'bill_import_taxable': bill_import_taxable,
            'bill_import_tax': bill_import_tax,
            'bill_fix_asset_tax': bill_fix_asset_tax,
            'total_vat_due': total_vat_due,
            'total_input_vat_credit': total_input_vat_credit,
            'tax_liability': tax_liability
        }

        _logger.info(
            '''
            
            =========<< Report Data for VAT Return Content >>=========
            %s
            
            ''' % report_data
        )

        return report_data

    def print_pdf_report(self):
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["model"] = "wizard.vat.return"
        datas["report_data"] = self.get_vat_return_data()
        datas["form"] = self.read()[0]

        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref(
            "atw_tax_reports.vat_return_report"
        ).report_action(
            self, data=datas
        )
