# -*- coding: utf-8 -*-
""" Account Bank Statement Line """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
from num2words import num2words


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    partner_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Delivery Address"
    )
    child_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Secondary Delivery Address"
    )

    # analytic_accounts_id = fields.Many2many(
    #     "account.analytic.account",
    #     string="Analytic Accounts"
    # )

    def write(self, vals):
        res = super().write(vals)

        if self.move_id:
            # Prepare analytic dist dic data
            # analytic_dict = {}
            # if self.line_ids and self.analytic_accounts_id:

            #     for analytic_ac in self.analytic_accounts_id:
            #         analytic_dict.update(
            #             {str(analytic_ac.id): 100.0})

            if self.cheque_no \
                    or self.partner_delivery_address_id or self.child_delivery_address_id:
                for line in self.move_id.line_ids:
                    # line.analytic_distribution = analytic_dict or None
                    line.cheque_no = self.cheque_no or None
                    line.partner_delivery_address_id = self.partner_delivery_address_id.id or None
                    line.child_delivery_address_id = self.child_delivery_address_id.id or None

        return res

    def update_cheque_journal_items(self):
        for rec in self:
            if rec.move_id and rec.cheque_no:
                for line in rec.move_id.line_ids:
                    line.cheque_no = rec.cheque_no or None

    def update_delivery_address_journal_items(self):
        for rec in self:
            if rec.move_id \
                    and (rec.partner_delivery_address_id or rec.child_delivery_address_id):
                for line in rec.move_id.line_ids:
                    line.partner_delivery_address_id = rec.partner_delivery_address_id.id or None
                    line.child_delivery_address_id = rec.child_delivery_address_id.id or None
