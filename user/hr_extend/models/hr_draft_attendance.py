from odoo import models, fields, api, _


class HrDraftAttendance(models.Model):
    _inherit = 'hr.draft.attendance'

    company_id = fields.Many2one(related="employee_id.company_id", string="Company", store=True)
