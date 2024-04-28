import base64
import logging
import os

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'


class ProductProductInh(models.Model):
    _inherit = 'product.product'
