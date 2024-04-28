# -*- coding: utf-8 -*-
""" Account Move """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import timedelta,date,datetime
import datetime
import xlsxwriter
import base64



from odoo.tools.misc import xlwt
from odoo.tools import base64_to_image
import tempfile
import io
from PIL import Image



class AccountMove(models.Model):
    """ inherit Account Move """
    _inherit = 'account.move'

    check_lock_pass = fields.Boolean(default=True)

    lpo = fields.Char()


    remaining_days = fields.Char(string="Remaining Days", compute='difference_date_remainig')
    remaining_days_count = fields.Integer(string="Remaining Days Count", compute='difference_date_remainig')
    

    # @api.depends('date','state','invoice_date')
    # def check_lock_pass_compute(self):
    #     for move in self:
    #         lock_date = move.company_id._get_user_fiscal_lock_date()
    #         if move.state=='posted':
    #             if lock_date:
    #                 if move.date <= lock_date:
    #                     move.check_lock_pass == True
    #                 else:
    #                     move.check_lock_pass == False

    #                 if move.invoice_date <= lock_date:
    #                     move.check_lock_pass == True
    #                 else:
    #                     move.check_lock_pass == False
    #         if move.state=='draft':
    #             move.check_lock_pass == False


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            lock_date = move.company_id._get_user_fiscal_lock_date()
            if lock_date:
                if move.move_type=='out_invoice' or move.move_type=='in_invoice' :
                    if move.invoice_date:
                        if move.invoice_date <= lock_date:
                            move.date = move.invoice_date
                            move.check_lock_pass = True
        return res

    def _check_fiscalyear_lock_date(self):
        for move in self:
            lock_date = move.company_id._get_user_fiscal_lock_date()
            if move.date <= lock_date:
                if move.check_lock_pass == True:
                    res = super(AccountMove, self)._check_fiscalyear_lock_date()
        return True


    # def button_draft_password(self):
    #     exchange_move_ids = set()
    #     if self:
    #         self.env['account.full.reconcile'].flush_model(['exchange_move_id'])
    #         self.env['account.partial.reconcile'].flush_model(['exchange_move_id'])
    #         self._cr.execute(
    #             """
    #                 SELECT DISTINCT sub.exchange_move_id
    #                 FROM (
    #                     SELECT exchange_move_id
    #                     FROM account_full_reconcile
    #                     WHERE exchange_move_id IN %s

    #                     UNION ALL

    #                     SELECT exchange_move_id
    #                     FROM account_partial_reconcile
    #                     WHERE exchange_move_id IN %s
    #                 ) AS sub
    #             """,
    #             [tuple(self.ids), tuple(self.ids)],
    #         )
    #         exchange_move_ids = set([row[0] for row in self._cr.fetchall()])

    #     for move in self:
    #         if move.id in exchange_move_ids:
    #             raise UserError(_('You cannot reset to draft an exchange difference journal entry.'))
    #         if move.tax_cash_basis_rec_id or move.tax_cash_basis_origin_move_id:
    #             # If the reconciliation was undone, move.tax_cash_basis_rec_id will be empty;
    #             # but we still don't want to allow setting the caba entry to draft
    #             # (it'll have been reversed automatically, so no manual intervention is required),
    #             # so we also check tax_cash_basis_origin_move_id, which stays unchanged
    #             # (we need both, as tax_cash_basis_origin_move_id did not exist in older versions).
    #             raise UserError(_('You cannot reset to draft a tax cash basis journal entry.'))
    #         if move.restrict_mode_hash_table and move.state == 'posted':
    #             raise UserError(_('You cannot modify a posted entry of this journal because it is in strict mode.'))
    #         # We remove all the analytics entries for this journal
    #         move.mapped('line_ids.analytic_line_ids').unlink()

    #     self.mapped('line_ids').remove_move_reconcile()
    #     self.write({'state': 'draft', 'is_move_sent': False})
               
    
    @api.depends('invoice_date_due')
    def difference_date_remainig(self):
        # fmt = '%Y-%m-%d'
        # today = date.today()
        for record in self:
            if record.invoice_date_due:
                delta = datetime.date.today() - record.invoice_date_due

                if delta.days > 0:
                    record.remaining_days = str(delta.days) + '  '+'Days';
                else:
                    record.remaining_days = 'Not Due';

                record.remaining_days_count = delta.days;
            else:
                record.remaining_days_count =0

                record.remaining_days =0

    @api.onchange('lpo')
    def _onchange_lpo(self):
        """ lpo """
        for rec in self:
            if rec.lpo:
                rec.ref = rec.lpo

    def action_check_lock_pass(self):
        """ :return Project Message action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'check.lock.pass',
            'name': _('Inter Pass'),
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
        }

    @api.constrains('ref')
    def _check_unique_bill_reference(self):
        for record in self:
            if record.move_type == 'in_invoice':
                if record.ref:
                    duplicates = self.env['account.move'].search(
                        [('ref', '=', record.ref),('partner_id','=',record.partner_id.id), ('id', '!=', record.id)])
                    if duplicates:
                        raise ValidationError(
                            'The bill reference must be unique!')

    # @api.onchange('invoice_date')
    # def _onchange_invoice_lock_date(self):
    #     """ invoice_date """
    #     for rec in self:
    #         if rec.invoice_date and not rec.check_lock_pass:
    #             rec.check_lock_pass = True

    @api.model
    def create(self, vals):
        """ Override create() """

        res = super(AccountMove, self).create(vals)
        res.check_lock_pass = False
        return res


class AccountMoveLine(models.Model):
    """ inherit Account Move Line """
    _inherit = 'account.move.line'

    discount_fixed = fields.Float(string="Discount Amount")
    global_percent_discount = fields.Float()
    global_amount_discount = fields.Float()

    lpo = fields.Char(related='move_id.lpo')
    # lpo = fields.Char(cmpute='compute_lpo')
    partner_delivery_address_id = fields.Many2one('res.partner',compute='compute_delivery_address')




    analytic_name = fields.Text(related='move_id.analytic_name')


    @api.onchange('discount', 'quantity', 'price_unit', 'product_id')
    def _onchange_discount_percent(self):
        """ discount_percent """
        if self.discount:
            total = self.quantity * self.price_unit
            if total > 0:
                self.discount_fixed = (self.discount * total) / 100

    @api.onchange('discount_fixed', 'quantity', 'price_unit',
                  'product_id')
    def _onchange_discount_fixed(self):
        """ discount_percent """
        if self.discount_fixed:
            total = self.quantity * self.price_unit
            if total > 0:
                self.discount = (self.discount_fixed / total) * 100



    # @api.depends('move_id.lpo')
    # def compute_lpo(self):
    #     for rec in self:
    #         rec.lpo = rec.move_id.lpo



    @api.depends('move_id.partner_delivery_address_id')
    def compute_delivery_address(self):
        for rec in self:
            rec.partner_delivery_address_id = rec.move_id.partner_delivery_address_id.id


    remaining_days = fields.Char(string="Remaining Days", compute='difference_date_remainig')
    remaining_days_count = fields.Integer(string="Remaining Days Count", compute='difference_date_remainig')
    

   




    
    @api.depends('date_maturity')
    def difference_date_remainig(self):
        # fmt = '%Y-%m-%d'
        # today = date.today()
        for record in self:
            if record.date_maturity:
                # d1 = datetime.strptime(today, '%Y-%m-%d')

                # d2 = datetime.strptime(record.date_maturity, '%Y-%m-%d')
                # record.remaining_days =str(record/.date_maturity)
                # record.remaining_days =str((d2-d1).days)
                delta = datetime.date.today() - record.date_maturity

                    # print(delta.days)
                if delta.days > 0:
                    record.remaining_days = str(delta.days) + '  '+'Days';
                else:
                    record.remaining_days = 'Not Due';

                record.remaining_days_count = delta.days;
            else:
                record.remaining_days_count =0

                record.remaining_days =0




class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    def generate_excel_report(self):


        self.ensure_one()
        file_path = 'Partner Details report' + '.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)

        title_format = workbook.add_format(
            {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 11, 'bg_color': '#D8D8D8'})

        formate_1 = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 11,'font_color':'red'})

        # record = self.env['account.analytic.line'].search(
        #     [('employee_id', 'in', self.employee_ids.ids), ('date', '>=', self.start_date),
        #      ('date', '<=', self.end_date)])

        sheet = workbook.add_worksheet('Partner Details Report')

        row = 8
        col = 2
        total = 0

        grouped_records = {}
        for rec in self:
            partner_id = rec['name']
            if partner_id in grouped_records:
                grouped_records[partner_id].append(rec)
            else:
                grouped_records[partner_id] = [rec]

        sheet.set_column('A:A', 13)
        sheet.set_column('B:C', 25)
        sheet.set_column('D:E', 25)
        sheet.set_column('F:G', 25)
        sheet.set_column('G:H', 25)
        sheet.set_column('I:I', 18)

        # sheet.set_column('C:C', 13)
        # sheet.set_column('D:E', 25)
        # sheet.set_column('E:F', 25)
        # sheet.set_column('G:G', 18)

     






        delivery_address = []
        unique_numbers = set(self.unreconciled_aml_ids.partner_delivery_address_id)
        for da in unique_numbers:
            delivery_address.append(da)

        row_t = 1
        col_t = 4
        for record in self:
            sheet.merge_range(row_t, col_t-1, row_t + 1, col_t + 1, record.company_id.name, title_format)
        # sheet.merge_range(row - 4, 3, row - 4, 5, f' Timesheet Period : From {self.start_date} To {self.end_date}',title_format)

        store_list = []
        for rec in self:
            if rec:
                store_list.append({'id': rec.id, 'name': rec.name})

        for emp_name in store_list:
            sheet.merge_range(row - 4, 0, row - 4, 1, f" Partner Name : {emp_name['name']}", title_format)
            # if emp_name['name'] in [i.name for i in grouped_records]:
            # for employee_id, employee_records in grouped_records.items():

        for record in self:
            # if employee_id.name == emp_name['partner_id']:
            sheet.write(row-1, 0, 'Date', title_format)
            sheet.write(row-1, 1, 'Invoic', title_format)
            sheet.write(row-1, 2, 'Due Date', title_format)
            sheet.write(row-1, 3, 'Analytic Account', title_format)
            sheet.write(row-1, 4, 'delivery Address', title_format)
            sheet.write(row-1, 5, 'LPO', title_format)
            sheet.write(row-1, 6, 'Age', title_format)
            sheet.write(row-1, 7, 'Resaidual Amount', title_format)
            sheet.write(row-1, 8, 'Total Amount', title_format)
            total=0
            total_r=0

            for address in delivery_address:
                if address:

                    st=0
                    st_r=0
                    

                    sheet.merge_range(row, 0, row, 8, f"{address['name']}", title_format)
                    
                    for rec in sorted((record.unreconciled_aml_ids), key=lambda r: r['remaining_days_count'], reverse=True):
                        if rec.partner_delivery_address_id.id== address.id:
                            st+=rec.amount_currency
                            st_r+=rec.amount_residual_currency
                            row += 1
                            if rec.date :
                                sheet.write(row, 0, rec.date.strftime("%Y-%m-%d"))
                            else :
                                sheet.write(row, 0, '')
                            if rec.move_name :
                                sheet.write(row, 1, rec.move_name)
                            else :
                                sheet.write(row, 1, '')
                            if rec.date_maturity :
                                sheet.write(row, 2, rec.date_maturity.strftime("%Y-%m-%d"))
                            else :
                                sheet.write(row, 2, '')
                            if rec.analytic_name :
                                sheet.write(row, 3, rec.analytic_name)
                            else :
                                sheet.write(row, 3, '')
                            if rec.partner_delivery_address_id :
                                sheet.write(row, 4, rec.partner_delivery_address_id.name)
                            else :
                                sheet.write(row, 4, '')
                            if rec.lpo :
                                sheet.write(row, 5, rec.lpo)
                            else :
                                sheet.write(row, 5, '')
                            if rec.remaining_days :
                                sheet.write(row, 6, rec.remaining_days)
                            else :
                                sheet.write(row, 6, '')
                            if rec.amount_residual_currency :
                                sheet.write(row, 7, rec.amount_residual_currency)
                            else :
                                sheet.write(row, 7, '')
                            if rec.amount_currency :
                                sheet.write(row, 8, rec.amount_currency)
                            else :
                                sheet.write(row, 8, '')
                    row += 1



                     

                    sheet.write(row, 0, '',title_format) 
                    sheet.write(row, 1, '',title_format) 
                    sheet.write(row, 2, '',title_format) 
                    sheet.write(row, 3, 'Total',title_format) 
                    sheet.write(row, 4, '',title_format) 
                    sheet.write(row, 5, '',title_format) 
                    sheet.write(row, 6, '',title_format) 
                    sheet.write(row, 7, st_r,title_format) 
                    sheet.write(row, 8, st ,title_format)
                    row += 2


            sheet.merge_range(row+1 , 0, row+1, 8, "", title_format)
            row +=1
            
            st=0
            st_r=0
            for rec in sorted((record.unreconciled_aml_ids), key=lambda r: r['remaining_days_count'], reverse=True):

                if not rec.partner_delivery_address_id:
                    st+=rec.amount_currency
                    st_r+=rec.amount_residual_currency

                    row += 1

                    if rec.date :
                        sheet.write(row, 0, rec.date.strftime("%Y-%m-%d"))
                    else :
                        sheet.write(row, 0, '')
                    if rec.move_name :
                        sheet.write(row, 1, rec.move_name)
                    else :
                        sheet.write(row, 1, '')
                    if rec.date_maturity :
                        sheet.write(row, 2, rec.date_maturity.strftime("%Y-%m-%d"))
                    else :
                        sheet.write(row, 2, '')
                    if rec.analytic_name :
                        sheet.write(row, 3, rec.analytic_name)
                    else :
                        sheet.write(row, 3, '')
                    if rec.partner_delivery_address_id :
                        sheet.write(row, 4, rec.partner_delivery_address_id.name)
                    else :
                        sheet.write(row, 4, '')
                    if rec.lpo :
                        sheet.write(row, 5, rec.lpo)
                    else :
                        sheet.write(row, 5, '')
                    if rec.remaining_days :
                        sheet.write(row, 6, rec.remaining_days)
                    else :
                        sheet.write(row, 6, '')
                    if rec.amount_residual_currency :
                        sheet.write(row, 7, rec.amount_residual_currency)
                    else :
                        sheet.write(row, 7, '')
                    if rec.amount_currency :
                        sheet.write(row, 8, rec.amount_currency)
                    else :
                        sheet.write(row, 8, '')
                



                 

            sheet.write(row+1, 0, '',title_format) 
            sheet.write(row+1, 1, '',title_format) 
            sheet.write(row+1, 2, '',title_format) 
            sheet.write(row+1, 3, 'Total',title_format) 
            sheet.write(row+1, 4, '',title_format) 
            sheet.write(row+1, 5, '',title_format) 
            sheet.write(row+1, 6, '',title_format) 
            sheet.write(row+1, 7, st_r,title_format) 
            sheet.write(row+1, 8, st ,title_format)
            row += 2


                 

        sheet.write(row+2, 0, '',title_format) 
        sheet.write(row+2, 1, '',title_format) 
        sheet.write(row+2, 2, '',title_format) 
        sheet.write(row+2, 3, 'Total Due',title_format) 
        sheet.write(row+2, 4, '',title_format) 
        sheet.write(row+2, 5, '',title_format) 
        sheet.write(row+2, 6, '',title_format) 
        sheet.write(row+2, 7, '' ,title_format) 
        sheet.write(row+2, 8, record.total_due ,title_format) 
                 

        sheet.write(row+4, 0, '',title_format) 
        sheet.write(row+4, 1, '',title_format) 
        sheet.write(row+4, 2, '',title_format) 
        sheet.write(row+4, 3, 'Total Overdue',title_format) 
        sheet.write(row+4, 4, '',title_format) 
        sheet.write(row+4, 5, '',title_format) 
        sheet.write(row+4, 6, '',title_format) 
        sheet.write(row+4, 7, '' ,title_format) 
        sheet.write(row+4, 8, record.total_overdue ,title_format)
                # row += 4
                # total=0
        # else:
        #     sheet.merge_range(row , 3, row , 5,"No Data Was Found For This Employee In Selected Date", formate_1)
        #     row += 4



        workbook.close()
        ex_report = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())

        excel_report_id = self.env['save.ex.report.wizard'].create({"document_frame": file_path,
                                                                    "file_name": ex_report})

        return {
            'res_id': excel_report_id.id,
            'name': 'Files to Download',
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': False,
            'res_model': 'save.ex.report.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def generate_excel_report_invoices(self):


        self.ensure_one()
        file_path = 'Partner Invoices Details report' + '.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)

        title_format = workbook.add_format(
            {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 11, 'bg_color': '#D8D8D8'})

        formate_1 = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 11,'font_color':'red'})

        # record = self.env['account.analytic.line'].search(
        #     [('employee_id', 'in', self.employee_ids.ids), ('date', '>=', self.start_date),
        #      ('date', '<=', self.end_date)])

        sheet = workbook.add_worksheet('Partner Invoices Details Report')

        row = 8
        col = 2
        total = 0

        grouped_records = {}
        for rec in self:
            partner_id = rec['name']
            if partner_id in grouped_records:
                grouped_records[partner_id].append(rec)
            else:
                grouped_records[partner_id] = [rec]

        sheet.set_column('A:A', 13)
        sheet.set_column('B:C', 25)
        sheet.set_column('D:E', 25)
        sheet.set_column('F:G', 25)
        sheet.set_column('G:H', 25)
        sheet.set_column('I:I', 18)

        # sheet.set_column('C:C', 13)
        # sheet.set_column('D:E', 25)
        # sheet.set_column('E:F', 25)
        # sheet.set_column('G:G', 18)

     






        delivery_address = []
        unique_numbers = set(self.unpaid_invoice_ids.partner_delivery_address_id)
        for da in unique_numbers:
            delivery_address.append(da)






        row_t = 1
        col_t = 4
        for record in self:
            sheet.merge_range(row_t, col_t-1, row_t + 1, col_t + 1, record.company_id.name, title_format)
        # sheet.merge_range(row - 4, 3, row - 4, 5, f' Timesheet Period : From {self.start_date} To {self.end_date}',title_format)

        store_list = []
        for rec in self:
            if rec:
                store_list.append({'id': rec.id, 'name': rec.name})

        for emp_name in store_list:
            sheet.merge_range(row - 4, 0, row - 4, 1, f" Partner Name : {emp_name['name']}", title_format)
            # if emp_name['name'] in [i.name for i in grouped_records]:
            # for employee_id, employee_records in grouped_records.items():
        total_amount=0
        amount_residual =0

        for record in self:
            # if employee_id.name == emp_name['partner_id']:
            sheet.write(row-1, 0, 'Date', title_format)
            sheet.write(row-1, 1, 'Invoic', title_format)
            sheet.write(row-1, 2, 'Due Date', title_format)
            sheet.write(row-1, 3, 'Analytic Account', title_format)
            sheet.write(row-1, 4, 'delivery Address', title_format)
            sheet.write(row-1, 5, 'LPO', title_format)
            sheet.write(row-1, 6, 'Age', title_format)
            sheet.write(row-1, 7, 'Resaidual Amount', title_format)
            sheet.write(row-1, 8, 'Total Amount', title_format)
            total=0
            total_r=0

            for address in delivery_address:
                if address:

                    st=0
                    st_r=0
                    

                    sheet.merge_range(row, 0, row, 8, f"{address['name']}", title_format)
                    for rec in sorted((record.unpaid_invoice_ids), key=lambda r: r['remaining_days_count'], reverse=True):
                        if rec.partner_delivery_address_id.id== address.id:
                            row += 1
                            st+=rec.amount_total_in_currency_signed
                            st_r+=rec.amount_residual_signed
                            if rec.date :
                                sheet.write(row, 0, rec.date.strftime("%Y-%m-%d"))
                            else :
                                sheet.write(row, 0, '')
                            if rec.name :
                                sheet.write(row, 1, rec.name)
                            else :
                                sheet.write(row, 1, '')
                            if rec.invoice_date_due :
                                sheet.write(row, 2, rec.invoice_date_due.strftime("%Y-%m-%d"))
                            else :
                                sheet.write(row, 2, '')
                            if rec.analytic_name :
                                sheet.write(row, 3, rec.analytic_name)
                            else :
                                sheet.write(row, 3, '')
                            if rec.partner_delivery_address_id :
                                sheet.write(row, 4, rec.partner_delivery_address_id.name)
                            else :
                                sheet.write(row, 4, '')
                            if rec.lpo :
                                sheet.write(row, 5, rec.lpo)
                            else :
                                sheet.write(row, 5, '')
                            if rec.remaining_days :
                                sheet.write(row, 6, rec.remaining_days)
                            else :
                                sheet.write(row, 6, '')
                            if rec.amount_residual_signed :
                                sheet.write(row, 7, rec.amount_residual_signed)
                            else :
                                sheet.write(row, 7, '')
                            if rec.amount_total_in_currency_signed :
                                sheet.write(row, 8, rec.amount_total_in_currency_signed)
                            else :
                                sheet.write(row, 8, '')
                            total_amount +=rec.amount_total_in_currency_signed
                            amount_residual +=rec.amount_residual_signed
                    row += 1



                 

                    sheet.write(row, 0, '',title_format) 
                    sheet.write(row, 1, '',title_format) 
                    sheet.write(row, 2, '',title_format) 
                    sheet.write(row, 3, 'Total',title_format) 
                    sheet.write(row, 4, '',title_format) 
                    sheet.write(row, 5, '',title_format) 
                    sheet.write(row, 6, '',title_format) 
                    sheet.write(row, 7, st_r,title_format) 
                    sheet.write(row, 8, st ,title_format)
                    row += 2


            sheet.merge_range(row+1 , 0, row+1, 8, "", title_format)
            row +=1
            
            st=0
            st_r=0
            for rec in sorted((record.unpaid_invoice_ids), key=lambda r: r['remaining_days_count'], reverse=True):

                if not rec.partner_delivery_address_id:
                    st+=rec.amount_total_in_currency_signed
                    st_r+=rec.amount_residual_currency

                    row += 1

                    if rec.date :
                        sheet.write(row, 0, rec.date.strftime("%Y-%m-%d"))
                    else :
                        sheet.write(row, 0, '')
                    if rec.move_name :
                        sheet.write(row, 1, rec.move_name)
                    else :
                        sheet.write(row, 1, '')
                    if rec.date_maturity :
                        sheet.write(row, 2, rec.date_maturity.strftime("%Y-%m-%d"))
                    else :
                        sheet.write(row, 2, '')
                    if rec.analytic_name :
                        sheet.write(row, 3, rec.analytic_name)
                    else :
                        sheet.write(row, 3, '')
                    if rec.partner_delivery_address_id :
                        sheet.write(row, 4, rec.partner_delivery_address_id.name)
                    else :
                        sheet.write(row, 4, '')
                    if rec.lpo :
                        sheet.write(row, 5, rec.lpo)
                    else :
                        sheet.write(row, 5, '')
                    if rec.remaining_days :
                        sheet.write(row, 6, rec.remaining_days)
                    else :
                        sheet.write(row, 6, '')
                    if rec.amount_residual_currency :
                        sheet.write(row, 7, rec.amount_residual_currency)
                    else :
                        sheet.write(row, 7, '')
                    if rec.amount_currency :
                        sheet.write(row, 8, rec.amount_currency)
                    else :
                        sheet.write(row, 8, '')
                    total_amount +=rec.amount_total_in_currency_signed
                    amount_residual +=rec.amount_residual_signed
                    



                     

            sheet.write(row+1, 0, '',title_format) 
            sheet.write(row+1, 1, '',title_format) 
            sheet.write(row+1, 2, '',title_format) 
            sheet.write(row+1, 3, 'Total',title_format) 
            sheet.write(row+1, 4, '',title_format) 
            sheet.write(row+1, 5, '',title_format) 
            sheet.write(row+1, 6, '',title_format) 
            sheet.write(row+1, 7, st_r,title_format) 
            sheet.write(row+1, 8, st ,title_format)
            row += 2


                 

        sheet.write(row+2, 0, '',title_format) 
        sheet.write(row+2, 1, '',title_format) 
        sheet.write(row+2, 2, '',title_format) 
        sheet.write(row+2, 3, 'Total Due',title_format) 
        sheet.write(row+2, 4, '',title_format) 
        sheet.write(row+2, 5, '',title_format) 
        sheet.write(row+2, 6, '',title_format) 
        sheet.write(row+2, 7, '' ,title_format) 
        sheet.write(row+2, 8, amount_residual ,title_format) 
                 

        sheet.write(row+4, 0, '',title_format) 
        sheet.write(row+4, 1, '',title_format) 
        sheet.write(row+4, 2, '',title_format) 
        sheet.write(row+4, 3, 'Total Amount',title_format) 
        sheet.write(row+4, 4, '',title_format) 
        sheet.write(row+4, 5, '',title_format) 
        sheet.write(row+4, 6, '',title_format) 
        sheet.write(row+4, 7, '' ,title_format) 
        sheet.write(row+4, 8, total_amount ,title_format)
                # row += 4
                # total=0
        # else:
        #     sheet.merge_range(row , 3, row , 5,"No Data Was Found For This Employee In Selected Date", formate_1)
        #     row += 4



        workbook.close()
        ex_report = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())

        excel_report_id = self.env['save.ex.report.wizard'].create({"document_frame": file_path,
                                                                    "file_name": ex_report})

        return {
            'res_id': excel_report_id.id,
            'name': 'Files to Download',
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': False,
            'res_model': 'save.ex.report.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }














