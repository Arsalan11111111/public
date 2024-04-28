
from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    analytic_accounts_id = fields.Many2many(
        "account.analytic.account",
        string="Analytic Accounts"
    )
