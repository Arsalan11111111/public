from odoo.exceptions import AccessError, ValidationError
import pytz
from datetime import timedelta
from collections import defaultdict
from datetime import datetime, date, time
from odoo import api, fields, models, _

class HrSalaryAttachment(models.Model):
    _inherit = 'hr.employee'

    grade = fields.Char("Employee Grade")