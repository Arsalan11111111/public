import base64
import logging
import os

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'
