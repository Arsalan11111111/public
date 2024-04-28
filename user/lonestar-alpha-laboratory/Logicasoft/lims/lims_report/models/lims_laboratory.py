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
from odoo import fields, models
from datetime import datetime, timedelta


class LimsLaboratory(models.Model):
    _inherit = 'lims.laboratory'

    def domain_report_signatory(self):
        group_validate_report_id = self.env.ref('lims_report.group_lims_validate_report')
        return [('id', 'in', group_validate_report_id.users.ids)]

    seq_report_id = fields.Many2one('ir.sequence', 'Sequence Report', index=True)
    text_subcontracted = fields.Html('Text for subcontracted', translate=True)
    lock_analysis_state_report = fields.Selection('get_state_selection', default='validated', string='Lock analysis from reports',
                                                  help='Lock the analysis when the report is in this stage')
    note_report = fields.Html('Note report', translate=True)
    note_report_draft = fields.Html('Note report when draft', translate=True)
    note_report_validated = fields.Html('Note report when validated', translate=True)
    note_report_cancelled = fields.Html('Note report when cancelled', translate=True)
    report_signatory_1_id = fields.Many2one('res.users', 'Default signatory 1', domain=domain_report_signatory,
                                            help='Default signatory 1 when a report is created')
    report_signatory_2_id = fields.Many2one('res.users', 'Default signatory 2', domain=domain_report_signatory,
                                            help='Default signatory 2 when a report is created')

    default_report_template = fields.Many2one('lims.analysis.report.template',
                                              help='Defines the report template that will be proposed by default when '
                                                   'creating a report for LIMS.')

    note_report_replaced = fields.Html('Note report when replaced',
                                       help='Comment of report when the report replace a previous report', translate=True)

    def get_state_selection(self):
        states = self.env['lims.analysis.report'].get_state_selection()
        return [state for state in states if 'cancel' not in state]

    def get_default_report_model_id(self):
        """
        Get ir.actions.report from report template define in laboratory.

        :return:
        """
        report = False
        if self.default_report_template:
            report = self.default_report_template.report_id
        return report

