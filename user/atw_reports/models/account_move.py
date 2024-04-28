import base64
import logging
import os

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'odoo.logger']

    our_ref = fields.Char("Our Ref", copy=False, tracking=1)
    project_job_number = fields.Char("Project/Job No.", copy=False, tracking=1)

    last_payment_date = fields.Date(
        'Last Payment Date',
        compute='get_last_paydate',
        tracking=1,
    )

    @api.depends('amount_residual', 'invoice_payments_widget')
    def get_last_paydate(self):
        AccountPayment = self.env['account.payment']
        for invoice in self:
            invoice.last_payment_date = None
            payments_widget = invoice.invoice_payments_widget
            if payments_widget and payments_widget.get('content'):
                self.odoolog(
                    "Payment Content", payments_widget.get('content')
                )
                for content in payments_widget.get('content'):
                    payment = AccountPayment.browse(
                        content['account_payment_id'])
                    if payment:
                        invoice.last_payment_date = payment.date
                    else:
                        invoice.last_payment_date = content['date']

    project_name = fields.Char('Project', tracking=1)
