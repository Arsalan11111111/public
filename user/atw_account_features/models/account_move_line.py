from odoo import _, fields, models, api
from odoo.osv import expression
import logging

import re
from collections import Counter

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'odoo.logger']

    @api.onchange('product_id')
    def get_analytic_accounts(self):
        if self.product_id.analytic_accounts_id:
            analytic_dist = {}
            for analytic_account_id in self.product_id.analytic_accounts_id:
                analytic_dist.update({
                    str(analytic_account_id.id): 100.0
                })
            self.analytic_distribution = analytic_dist

    partner_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Primary Delivery Address",
        compute="get_delivery_address",
        store=True
    )
    child_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Secondary Delivery Address",
        compute="get_delivery_address",
        store=True
    )

    @api.depends(
        'move_id.partner_delivery_address_id',
        'move_id.child_delivery_address_id'
    )
    def get_delivery_address(self):
        for aml in self:
            if aml.partner_id:
                aml.partner_delivery_address_id = aml.move_id.partner_delivery_address_id
                aml.child_delivery_address_id = aml.move_id.child_delivery_address_id
            else:
                aml.partner_delivery_address_id = None
                aml.child_delivery_address_id = None
