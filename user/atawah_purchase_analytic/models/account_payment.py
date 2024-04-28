# -*- coding: utf-8 -*-
""" Account Payment """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class AccountPayment(models.Model):
    """ inherit Account Payment """
    _inherit = 'account.payment'

    address = fields.Text(
        string="Address",
        # compute="_compute_address"
    )
    payment_ref = fields.Char(default='NEW', string="Ref")
    cheque_no = fields.Char()

    def action_post(self):
        """ inherit action_post() """
        res = super(AccountPayment, self).action_post()
        self.payment_ref = self.env['ir.sequence'].next_by_code(
            'account.payment.ref') or '/'

    @api.depends('partner_id')
    # def _compute_address(self):
    #     for rec in self:
    #         res = [rec.partner_id.street, rec.partner_id.street2,
    #                rec.partner_id.city,
    #                rec.partner_id.zip]
    #         self.address = ', '.join(filter(bool, res))
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(
            x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
        else:
            liquidity_amount_currency = 0.0

        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(
            x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(
            x[1] for x in self._get_counterpart_aml_display_name_list())

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'cheque_no': self.cheque_no,
                'account_id': self.outstanding_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'cheque_no': self.cheque_no,
                'account_id': self.destination_account_id.id,
            },
        ]
        return line_vals_list + write_off_line_vals_list

    partner_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Delivery Address"
    )
    child_delivery_address_id = fields.Many2one(
        'res.partner',
        string="Delivery Address"
    )

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
