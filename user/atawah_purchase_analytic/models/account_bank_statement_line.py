# -*- coding: utf-8 -*-
""" Account Bank Statement Line """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
from num2words import num2words


class AccountBankStatementLine(models.Model):
    """ inherit Account Bank Statement Line """
    _inherit = 'account.bank.statement.line'

    address = fields.Char()
    default_account_id = fields.Many2one('account.account',
                                         compute='_compute_default_account_id',
                                         store=True)
    ref = fields.Char(default='New')
    cheque_no = fields.Char()
    invoices = fields.Char(compute='_compute_name_invoices', store=True)
    second_account_id = fields.Many2one('account.account',
                                        compute='_compute_name_invoices',
                                        store=True)
    partner_delivery_address_id = fields.Many2one('res.partner',
                                                  string="Delivery Address")
    child_delivery_address_id = fields.Many2one('res.partner',
                                                string=".")
    after_amount = fields.Float(compute='_compute_after_amount', store=True)


    # @api.onchange('ref','cheque_no')
    # def uniq_val(self):
    #     search_ref = self.env['account.bank.statement.line'].search([('ref','=',self.ref)])
    #     search_cheque_no = self.env['account.bank.statement.line'].search([('cheque_no','=',self.cheque_no),('cheque_no','!=','')])
    #     if search_ref:
    #         raise UserError('Ref already exist')
    #     if search_cheque_no:
    #         raise UserError('Cheque No already exist')
    #
    # _sql_constraints = [
    #     ('uniq_ref', 'UNIQUE(ref)', 'A follow-up action ref must be unique. This name is already set to another action.'),
    #     ('uniq_cheque_no', 'UNIQUE(cheque_no)', 'A follow-up action Cheque No must be unique. This name is already set to another action.'),
    # ]

    def _prepare_move_line_default_vals(self, counterpart_account_id=None):
        """ Prepare the dictionary to create the default account.move.lines for the current account.bank.statement.line
        record.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        """
        self.ensure_one()

        if not counterpart_account_id:
            counterpart_account_id = self.journal_id.suspense_account_id.id

        if not counterpart_account_id:
            raise UserError(_(
                "You can't create a new statement line without a suspense account set on the %s journal.",
                self.journal_id.display_name,
            ))

        company_amount, _company_currency, journal_amount, journal_currency, transaction_amount, foreign_currency \
            = self._get_amounts_with_currencies()

        liquidity_line_vals = {
            'name': self.payment_ref,
            'move_id': self.move_id.id,
            'cheque_no': self.cheque_no,
            'partner_id': self.partner_id.id,
            'account_id': self.journal_id.default_account_id.id,
            'currency_id': journal_currency.id,
            'amount_currency': journal_amount,
            'debit': company_amount > 0 and company_amount or 0.0,
            'credit': company_amount < 0 and -company_amount or 0.0,
        }

        # Create the counterpart line values.
        counterpart_line_vals = {
            'name': self.payment_ref,
            'account_id': counterpart_account_id,
            'cheque_no': self.cheque_no,
            'move_id': self.move_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': foreign_currency.id,
            'amount_currency': -transaction_amount,
            'debit': -company_amount if company_amount < 0.0 else 0.0,
            'credit': company_amount if company_amount > 0.0 else 0.0,
        }
        return [liquidity_line_vals, counterpart_line_vals]

    @api.depends('amount')
    def _compute_after_amount(self):
        """ Compute after_amount value """
        for rec in self:
            if rec.amount < 0:
                rec.after_amount = rec.amount * -1
            else:
                rec.after_amount = rec.amount

    def get_amount_in_word(self, amount):
        """ Get Amount In Word """
        lang = self.env.user.lang
        currency = self.currency_id
        text = ''
        if lang == 'en_US':
            text += num2words(int((str(amount).split('.')[0])),
                              lang='en') + ' ' + currency.currency_unit_label + '  '
            text += num2words(int((str(amount).split('.')[1])),
                              lang='en') + ' ' + currency.currency_subunit_label
        return text.title()

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

    @api.depends('name', 'partner_id')
    def _compute_name_invoices(self):
        """ Compute name_invoices value """
        for rec in self:
            invoices = self.env['account.move.line'].search(
                [('move_name', '=', rec.name)])
            if invoices:
                for i in invoices:
                    if i.account_id != rec.default_account_id:
                        rec.invoices = i.name
                        rec.second_account_id = i.account_id.id

    def get_old(self):
        """ Get Old """
        statement = self.env['account.bank.statement.line'].search([])
        for rec in statement:
            invoices = self.env['account.move.line'].search(
                [('move_name', '=', rec.name)])
            if invoices:
                for i in invoices:
                    if i.account_id != rec.default_account_id:
                        rec.invoices = i.name
                        rec.second_account_id = i.account_id.id


    def get_old_check(self):
        """ Get Old Check """
        statement = self.env['account.bank.statement.line'].search([])
        for rec in statement:
            invoices = self.env['account.move.line'].search(
                [('move_name', '=', rec.name)])
            if invoices:
                for i in invoices:
                    i.cheque_no=rec.cheque_no
                    # if i.account_id != rec.default_account_id:
                    #     rec.invoices = i.name
                    #     rec.second_account_id = i.account_id.id

    @api.model
    def create(self, vals):
        """ Override create method to sequence name """
        if vals.get('ref', 'New') == 'New':
            vals['ref'] = self.env['ir.sequence'].next_by_code(
                'account.bank.statement.line') or '/'
        return super(AccountBankStatementLine, self).create(vals)

    @api.depends('journal_id')
    def _compute_default_account_id(self):
        """ Compute default_account_id value """
        for rec in self:
            if rec.journal_id:
                rec.default_account_id = rec.journal_id.default_account_id.id

    # @api.onchange('partner_id')
    # def _onchange_partner_id_address(self):
    #     """ partner_id """
    #     for rec in self:
    #         rec.address = rec.partner_id.street

    @api.onchange('partner_id')
    def _onchange_partner_delivery_addressid(self):
        """ Add domain to some filed """
        self.partner_delivery_address_id = False
        if self.partner_id:
            return {'domain': {
                'partner_delivery_address_id': [
                    ('parent_id', '=', self.partner_id.id)]
            }}
