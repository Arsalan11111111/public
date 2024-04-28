# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################
from odoo import _, api, fields, models


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    xlsx_library = fields.Selection([("xlsxwriter", "Xlsxwriter"), ("openpyxl", "Openpyxl")], default='xlsxwriter')
    xlsx_template = fields.Many2one('ir.attachment', string='Related attachment',
                                       domain=['|',
                                               ('mimetype', '=',
                                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                               ('mimetype', '=', 'application/vnd.ms-excel.sheet.macroEnabled.12')],
                                       help='Use only file with extension .xlsx')

    def _render_xlsx(self, report_ref, docids, data):
        if self.xlsx_library == 'openpyxl':
            report_sudo = self._get_report(report_ref)
            report_model_name = f"report.{report_sudo.report_name}"
            report_model = self.env[report_model_name]
            xlsx_template = self._get_xlsx_template()
            return (
                report_model.with_context(active_model=report_sudo.model
                                          ).sudo(False).create_xlsx_report(docids, data,
                                                                           library=self.xlsx_library,
                                                                           template_file=xlsx_template)
            )
        return super()._render_xlsx(report_ref, docids, data)

    def _get_xlsx_template(self):
        # Need to be implemented in a second time.
        return self.xlsx_template
