
from odoo import api, fields, models, tools, _
import re


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'odoo.logger']

    @api.onchange('partner_id')
    def get_terms_condition(self):
        if self.partner_id and self.partner_id.terms_condition:
            self.notes = self.partner_id.terms_condition
