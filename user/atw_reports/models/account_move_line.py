from odoo import _, fields, models, api
from odoo.osv import expression
import logging

import re
from collections import Counter

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'odoo.logger']

    project_name = fields.Char(
        'Project', tracking=1,
        compute='get_project',
        store=True
    )

    @api.depends(
        'move_id.project_name'
    )
    def get_project(self):
        for aml in self:
            if aml.move_id.project_name:
                aml.project_name = aml.move_id.project_name
            else:
                aml.project_name = None
