# -*- coding: utf-8 -*-

from odoo import models, fields, _, tools
from odoo.exceptions import UserError


class GenericTaxReportCustomHandler(models.AbstractModel):
    _inherit = 'account.generic.tax.report.handler'


    def _caret_options_initializer(self):
        res = super()._caret_options_initializer()
        generic_tax_reports = [{'name': _("Detail by Partner"), 'action': 'caret_option_tax_report_details'}] + res.get("generic_tax_report")
        res.update(generic_tax_report=generic_tax_reports)
        return res

    def caret_option_tax_report_details(self, options, params):
        report = self.env['account.report'].browse(options['report_id'])
        model, tax_id = report._get_model_info_from_id(params['line_id'])

        if model != 'account.tax':
            raise UserError(_("Cannot audit tax from another model than account.tax."))

        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        domain = [('account_tax_id','=',tax_id),('date','>=',date_from),('date','<=',date_to)]

        ctx = {'search_default_group_journal': 2, 'expand': 1}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tax Report Details'),
            'res_model': 'tax.report.partner.views',
            'views': [[self.env.ref('atw_tax_reports.tax_report_partner_form_view').id, 'list']],
            'domain': domain,
            'context': ctx,
        }

class tax_report_partner_views(models.Model) :
    _name = "tax.report.partner.views"
    _auto = False

    id = fields.Integer()
    date = fields.Date()
    journal_name = fields.Char()
    move_id = fields.Many2one(comodel_name='account.move', string='Journal Name', )
    move_name = fields.Char()
    partner_name = fields.Char()
    partner_vat = fields.Char()
    debit = fields.Float()
    credit = fields.Float()
    amount_tax = fields.Float()
    total_amount = fields.Float()
    account_tax_id = fields.Many2one(comodel_name='account.tax')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'tax_report_partner_views')
        _query = """CREATE OR REPLACE VIEW tax_report_partner_views as (
                    select move_line_id as id, 
                        date, journal_name, move_id, move_name, partner_name, partner_vat, 
                        sum(debit) "debit", sum(credit) "credit", 
                        (sum(balance) * max(y.real_amount) / 100) "amount_tax",
                        sum(balance) + (sum(balance) * max(y.real_amount) / 100) "total_amount", y.id "account_tax_id"
                    from (
                        select a.id "move_line_id", a.date, b.name "journal_name", c.id move_id, c.name "move_name", d.name "account_name", a.partner_id,
                            e.name "partner_name", e.vat "partner_vat", a."name" "label", a.debit, a.credit, a.tax_line_id, f.account_tax_id,
                            case when a.debit > 0 then a.debit
                                when a.credit > 0 then a.credit 
                            end "balance"
                        from account_move_line a
                        join account_journal b on a.journal_id = b.id
                        join account_move c on a.move_id = c.id
                        join account_account d on a.account_id = d.id
                        left join res_partner e on a.partner_id = e.id
                        join account_move_line_account_tax_rel f on a.id = f.account_move_line_id
                    ) z 
                    join account_tax y on z.account_tax_id = y.id
                    where 1=1 
                    group by move_line_id, date, journal_name, move_id, move_name, partner_name, partner_vat, y.id
                    )"""
        self.env.cr.execute(_query)