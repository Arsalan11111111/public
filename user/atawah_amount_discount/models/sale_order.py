# -*- coding: utf-8 -*-
""" Sale Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class SaleOrderLine(models.Model):
    """ inherit Sale Order Line """
    _inherit = 'sale.order.line'

    discount_fixed = fields.Float(string="Discount Amount")

    @api.onchange('discount', 'product_uom_qty', 'price_unit', 'product_id')
    def _onchange_discount_percent(self):
        """ discount_percent """
        if self.discount:
            total = self.product_uom_qty * self.price_unit
            if total > 0:
                self.discount_fixed = (self.discount * total) / 100

    @api.onchange('discount_fixed', 'quantity', 'price_unit',
                  'product_id')
    def _onchange_discount_fixed(self):
        """ discount_percent """
        if self.discount_fixed:
            total = self.product_uom_qty * self.price_unit
            if total > 0:
                self.discount = (self.discount_fixed / total) * 100
