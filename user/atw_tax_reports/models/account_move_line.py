# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMoveLine(models.Model) :
    _inherit = "account.move.line"

    def _getAmountTax(self):
        for rec in self :
            amount_tax = 0
            for tax in rec.tax_ids :
                amount_tax += tax.compute_all(rec.balance).get('taxes')[0].get('amount')
            rec.amount_tax = amount_tax
        return True

    partner_vat = fields.Char(related='partner_id.vat', readonly=True, string='Tax ID', )
    amount_tax = fields.Monetary(compute=_getAmountTax, readonly=True, string='AmountTax', )
