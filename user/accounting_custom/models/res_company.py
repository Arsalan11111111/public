import base64
import logging
import os

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'


    aged_partner_ext_days_range = fields.Boolean(
        'Get extensive days range in aged partner balance',
        default=True
    )