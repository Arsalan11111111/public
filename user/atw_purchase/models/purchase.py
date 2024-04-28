
from odoo import api, fields, models, tools, _
import re
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'odoo.logger']

    analytic_accounts_id = fields.Many2many(
        "account.analytic.account",
        string="Analytic Accounts"
    )

    def is_number(self, value):
        try:
            float_value = float(value)
            return True
        except TypeError:
            return False

    @api.onchange('analytic_accounts_id', 'order_line')
    def update_lines_analytic(self):
        if self.order_line and self.analytic_accounts_id:
            self.odoolog("Analytic Accounts", self.analytic_accounts_id)
            analytic_dist = {}

            for analytic_ac in self.analytic_accounts_id:
                try:
                    if not self.is_number(analytic_ac.id):
                        raise KeyError('No data for id: %s' % analytic_ac.id)
                    analytic_dist.update({str(analytic_ac.id): 100.0})
                except KeyError as e:
                    # Extract the ID from the error message using regular expressions
                    self.odoolog("KeyError Message for %s" % analytic_ac.id, e)
                    id_match = re.search(r'NewId_(\d+)', str(analytic_ac.id))
                    self.odoolog("ID Match", id_match)
                    if id_match:
                        alternative_id = id_match.group(1)
                        self.odoolog(
                            f"Alternative ID extracted: {alternative_id}")

                        analytic_dist.update({str(alternative_id): 100.0})
                    else:
                        self.odoolog(
                            "Error: Unable to extract alternative ID from the error message.", type='error'
                        )

            self.odoolog("Analytic Dist", analytic_dist)
            for line in self.order_line:
                line.analytic_distribution = analytic_dist
                self.odoolog(
                    "Analytic Dist of %s" %
                    line, line.analytic_distribution
                )

    need_approval = fields.Boolean(
        "Needs Approval",
        compute="check_approval_need",
        store=True
    )

    need_second_approval = fields.Boolean(
        "Need Second Approval",
        compute="compute_approval_need",
        store=True
    )

    state = fields.Selection(selection_add=[
        ('first_approval_requested', '1st Approval Req'),
        ('second_approval_requested', '2nd Approval Req'),
        ('approved', 'Approved')
    ])

    @api.depends('amount_total')
    def check_approval_need(self):
        for purchase in self:
            if self.env.company.rfq_multi_approval:
                if purchase.amount_total > 5000:
                    purchase.need_approval = True
                    purchase.need_second_approval = True
                elif purchase.amount_total > 500:
                    purchase.need_approval = True
                    purchase.need_second_approval = False
                else:
                    purchase.need_approval = False
                    purchase.need_second_approval = False
            else:
                purchase.need_approval = False
                purchase.need_second_approval = False

    def button_confirm(self):
        if self.env.company.rfq_multi_approval:
            if self.amount_total > 500:
                if self.state == 'approved':
                    self.odoolog("PO Confirmed...", self.state)
                    for order in self:
                        order.order_line._validate_analytic_distribution()
                        order._add_supplier_to_product()
                        if order._approval_allowed():
                            order.button_approve()
                        else:
                            order.write({'state': 'to approve'})
                        if order.partner_id not in order.message_partner_ids:
                            order.message_subscribe([order.partner_id.id])
                    return True
                else:
                    raise UserError(
                        "Please approve for this RFQ confirmation."
                    )
            else:
                self.odoolog("PO Confirmed... for less than 500", self.state)
                return super().button_confirm()
        else:
            return super().button_confirm()

    def request_first_approval(self):
        for purchase in self:
            purchase.state = 'first_approval_requested'

    def request_second_approval(self):
        for purchase in self:
            if purchase.state == 'first_approval_requested' and \
                    self.user_has_groups('atw_purchase.group_rfq_approver_l1'):
                purchase.state = 'second_approval_requested'
            else:
                raise UserError(
                    'Cannot request, contact first approval request users to make request for second level approval.'
                )

    def approve_request(self):
        for purchase in self:
            if purchase.amount_total > 5000 and purchase.state == 'second_approval_requested'\
                    and self.user_has_groups('atw_purchase.group_rfq_approver_l2'):
                self.odoolog("Approve request... > 5000",
                             purchase.amount_total)
                purchase.state = 'approved'

            elif round(purchase.amount_total) in range(500, 5001) and purchase.state in [
                'first_approval_requested', 'second_approval_requested'
            ] and (self.user_has_groups('atw_purchase.group_rfq_approver_l1')
                   or self.user_has_groups('atw_purchase.group_rfq_approver_l2')):
                self.odoolog("Approve request... between 500 to 5000",
                             purchase.amount_total)
                purchase.state = 'approved'
            elif purchase.amount_total < 500:
                purchase.state = 'approved'
            else:
                raise UserError(
                    'Cannot be approved, please make approval request or contact users with 2nd level approver access.'
                )
