# -*- coding: utf-8 -*-
""" Res Partner """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class ResPartner(models.Model):
    """ inherit Res Partner """
    _inherit = 'res.partner'

    notes = fields.Text(string='Terms and Conditions')
