# -*- coding: utf-8 -*-
""" Account Change Lock Date """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class AccountChangeLockDate(models.TransientModel):
    """ Account Change Lock Date """
    _inherit = 'account.change.lock.date'
    _description = 'Account Change Lock Date'

    lock_date_password = fields.Char()

    def _prepare_lock_date_values(self):
        return {
            'period_lock_date': self.period_lock_date,
            'fiscalyear_lock_date': self.fiscalyear_lock_date,
            'tax_lock_date': self.tax_lock_date,
            'lock_date_password': self.lock_date_password
        }


