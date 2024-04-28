# -*- coding: utf-8 -*-
""" Check Lock Pass """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class CheckLockPass(models.TransientModel):
    """ Check Lock Pass """
    _name = 'check.lock.pass'
    _description = 'Check Lock Pass'

    password = fields.Char()

    def confirm(self):
        """ Confirm """
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        account_move_id = self.env[active_model].browse(active_id)
        # raise UserError(_(account_move_id))
        if account_move_id.company_id.lock_date_password == self.password:
            account_move_id.check_lock_pass = False
            account_move_id.button_draft()
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'sticky': True,
                    'message': _("Invalid Pass")
                }
            }
