import base64
import logging
import os

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'




class PurchaseOrderLineInh(models.Model):
    _inherit = 'purchase.order.line'


    employee_id = fields.Many2one('hr.employee')






