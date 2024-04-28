from odoo import _, fields, models, api
from odoo.osv import expression
import logging

import re
from collections import Counter

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'odoo.logger']

    @api.onchange('partner_id')
    def onchange_customer_id(self):
        if self.partner_id:
            partner_shipping_ids = []
            partner_invoice_ids = []
            partner_shipping_ids = self.env['res.partner'].search(
                [('parent_id', '=', self.partner_id.id)])
            partner_invoice_ids = partner_shipping_ids

            return {
                'domain': {
                    'partner_shipping_id': [('id', 'in', partner_shipping_ids.ids)],
                    'partner_invoice_id': [('id', 'in', partner_invoice_ids.ids)],
                }
            }
