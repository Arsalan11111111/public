# -*- coding: utf-8 -*-
""" Account Move """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class AccountMove(models.Model):
    """ inherit Account Move """
    _inherit = 'account.move'

    address = fields.Char()

    @api.onchange('partner_id')
    def _onchange_partner_id_add(self):
        """ partner_id """
        for rec in self:
            rec.address = False
            if rec.partner_id:
                rec.address = rec.partner_id.street

    @api.onchange('line_ids')
    def _onchange_line_ids_address(self):
        """ line_ids """
        if self.line_ids:
            for line in self.line_ids:
                line.address = line.partner_id.street
                line.lpo = line.ref

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids_address(self):
        """ line_ids """
        if self.invoice_line_ids:
            for line in self.line_ids:
                line.address = line.partner_id.street
                line.lpo = line.ref


class AccountMoveLine(models.Model):
    """ inherit Account Move """
    _inherit = 'account.move.line'

    def _default_address(self):
        if self.partner_id:
            return self.partner_id.street

    lpo = fields.Char(default='LOP_test')
    address = fields.Char(default='address_test')
