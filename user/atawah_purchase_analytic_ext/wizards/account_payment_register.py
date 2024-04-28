# -*- coding: utf-8 -*-
""" Account Bank Statement Line """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
from num2words import num2words


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)

        moves = self.env['account.move'].browse(
            self._context.get('active_ids', []))
        filtered_moves = moves.filtered(
            lambda move: move.partner_delivery_address_id)
        if filtered_moves:
            filtered_moves = filtered_moves[0]
            payment_vals.update({
                'partner_delivery_address_id': filtered_moves.partner_delivery_address_id.id or None,
                'child_delivery_address_id': filtered_moves.child_delivery_address_id.id or None,
            })

        return payment_vals
