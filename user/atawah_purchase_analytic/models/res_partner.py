# -*- coding: utf-8 -*-
""" Res Partner """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class ResPartner(models.Model):
    """ inherit Res Partner """
    _inherit = 'res.partner'

    partner_orders_history_ids = fields.One2many('partner.orders.history',
                                                 'res_partner_id')
    child_vat = fields.Char()

    @api.depends('name', 'street')
    def name_get(self):
        res = []
        for record in self:
            if record.parent_id:
                name = record.name
                # if record.street:
                #     name = name
                res.append((record.id, name))
            else:
                name = record.name
                # if record.street:
                #     name = name + " (" + record.street + ")"
                res.append((record.id, name))
        return res


class PartnerOrdersHistory(models.Model):
    """ Partner Orders History """
    _name = 'partner.orders.history'
    _description = 'Partner Orders History'

    res_partner_id = fields.Many2one('res.partner')
    date = fields.Date()
    account_move_id = fields.Many2one('account.move', string="Invoice")
    partner_delivery_address_id = fields.Many2one('res.partner',
                                                  string="Delivery Address")
    child_delivery_address_id = fields.Many2one('res.partner',
                                                string=".")
    invoice = fields.Char()
