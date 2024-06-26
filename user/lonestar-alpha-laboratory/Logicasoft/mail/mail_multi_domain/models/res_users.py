# -*- coding: utf-8 -*-
# Copyright 2020 Subteno IT
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields

USER_READABLE_FIELDS = [
    'mail_user_alias_ids',
    'server_mail_id',
]

USER_WRITABLE_FIELDS = [
    'mail_user_alias_ids',
    'server_mail_id',
]


class ResUsers(models.Model):
    _inherit = 'res.users'

    mail_user_alias_ids = fields.One2many(
        comodel_name='mail.user.alias',
        inverse_name='user_id',
    )
    server_mail_id = fields.Many2one(
        string='Server Mail',
        comodel_name='ir.mail_server',
        help='The server mail used for the user if the configuration is split server mail by user',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + USER_READABLE_FIELDS + USER_WRITABLE_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + USER_WRITABLE_FIELDS
