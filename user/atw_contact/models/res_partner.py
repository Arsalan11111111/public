from odoo import _, fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    terms_condition = fields.Html("Terms & Condition", tracking=1)

    def action_view_partner_bank_journal_items(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_moves_all"
        )
        journal_items = self.env['account.move.line'].search([
            ('parent_state', '=', 'posted'),
            ('journal_id.type', '=', 'bank'),
            ('move_id.partner_id', '=', self.id),
            # '|', '&', ('account_id.account_type', '=', 'liability_payable'),
            # ('account_id.non_trade', '=', False),
            # '&', ('account_id.account_type', '=', 'asset_receivable'),
            # ('account_id.non_trade', '=', False)
        ])
        action['domain'] = [
            ('id', 'in', journal_items.ids)
        ]
        action['context'] = {
            'journal_type': 'bank',
            'search_default_posted': 1
        }
        return action
