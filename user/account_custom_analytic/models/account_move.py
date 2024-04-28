from odoo import _, fields, models, api
from odoo.osv import expression
import logging

import re
from collections import Counter

_logger = logging.getLogger(__name__)


class InhAccountMove(models.Model):
    _inherit = 'account.move'

    analytic_distribution = fields.Json(string="Analytic Account")
    analytic_precision = fields.Integer(store=False,
                                        default=lambda self: self.env[
                                            'decimal.precision'].precision_get(
                                            "Percentage Analytic"), )
    analytic_name = fields.Text(compute='_compute_analytic_distribution_name',
                                store=True)

    @api.depends('analytic_distribution')
    def _compute_analytic_distribution_name(self):
        """ Compute analytic_distribution_name value """
        for rec in self:
            rec.analytic_name = ""
            if rec.analytic_distribution:
                for a in rec.analytic_distribution:
                    n = self.env['account.analytic.account'].search(
                        [('id', '=', a)], limit=1)
                    if not rec.analytic_name:
                        rec.analytic_name = "(" + n.name + ")"
                    else:
                        rec.analytic_name = rec.analytic_name + "(" + n.name + ")"



class InhAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    
    @api.depends('product_id')
    def _compute_name(self):
        defaults = super(InhAccountMoveLine, self)._compute_name()
        for line in self:
            if line.move_id.move_type == 'out_invoice':
                line.name = line.product_id.name
       
        return defaults
  