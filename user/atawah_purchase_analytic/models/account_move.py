# -*- coding: utf-8 -*-
""" Account Move """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class AccountMove(models.Model):
    """ inherit Account Move """
    _inherit = 'account.move'

    delivery_address = fields.Char()

    partner_delivery_address_id = fields.Many2one('res.partner',
                                                  string="Primary Delivery Address")
    child_delivery_address_id = fields.Many2one('res.partner',
                                                string="Secondary Delivery Address")
    vat = fields.Char()

    @api.onchange('partner_id', 'partner_delivery_address_id',
                  'child_delivery_address_id')
    def _onchange_partner_id_vat(self):
        """ partner_id """
        for rec in self:
            if rec.partner_id:
                rec.vat = rec.partner_id.vat
            if rec.partner_delivery_address_id:
                rec.vat = rec.partner_delivery_address_id.child_vat
            if rec.child_delivery_address_id:
                rec.vat = rec.child_delivery_address_id.child_vat

    def action_post(self):
        """ inherit action_post() """
        res = super(AccountMove, self).action_post()
        if self.ref:
            if self.partner_delivery_address_id:
                self.ref = self.ref + "/" + self.partner_delivery_address_id.name
                if self.child_delivery_address_id:
                    self.ref = self.ref + "/" + self.child_delivery_address_id.name
        else:
            if self.partner_delivery_address_id:
                self.ref = self.partner_delivery_address_id.name
                if self.child_delivery_address_id:
                    self.ref = self.ref + "/" + self.child_delivery_address_id.name

        if self.partner_id:
            self.partner_id.write({'partner_orders_history_ids': [(0, 0, {
                'res_partner_id': self.partner_id.id,
                'date': fields.Date.today(),
                'account_move_id': self.id,
                'invoice': self.name,
                'partner_delivery_address_id': self.partner_delivery_address_id.id,
                'child_delivery_address_id': self.child_delivery_address_id.id})]})

    @api.onchange('partner_id')
    def _onchange_partner_delivery_address_id(self):
        """ Add domain to some filed """
        self.partner_delivery_address_id = False
        if self.partner_id:
            partners = self.env['res.partner'].search(
                [('parent_id', '=', self.partner_id.id)])
            if partners:
                for rec in partners:
                    rec.hide_parent = True
            return {'domain': {
                'partner_delivery_address_id': [
                    ('parent_id', '=', self.partner_id.id)]
            }}

    @api.onchange('partner_delivery_address_id')
    def _onchange_child_delivery_address_id(self):
        """ Add domain to some filed """
        self.child_delivery_address_id = False
        if self.partner_id:
            if self.partner_delivery_address_id:
                partners = self.env['res.partner'].search(
                    [('parent_id', '=', self.partner_delivery_address_id.id)])
                if partners:
                    for rec in partners:
                        rec.hide_parent = True
                return {'domain': {
                    'child_delivery_address_id': [
                        ('parent_id', '=', self.partner_delivery_address_id.id)]
                }}

    partner_name_only = fields.Char(
        related="partner_id.name",
        string="Partner Name",
        store=True
    )


class AccountMoveLine(models.Model):
    """ inherit Account Move Line """
    _inherit = 'account.move.line'

    cheque_no = fields.Char()
    payment_ref = fields.Char()
