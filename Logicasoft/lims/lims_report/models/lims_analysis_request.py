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
from odoo import fields, models, api


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    is_ok_for_report = fields.Boolean(compute='compute_is_ok_for_report',
                                      help="It is checked if one samples have at least one analysis.")
    analysis_report_ids = fields.One2many('lims.analysis.report', 'analysis_request_id')
    nb_reports = fields.Integer('Reports', compute='compute_nb_reports')
    date_report_sent = fields.Date('Date Report Sent', copy=False,
                                   help="This date is fulfilled on the moment one if his report is sent.")
    report_template_id = fields.Many2one('lims.analysis.report.template',
                                         help="This report-template will be used in the future flow of creating report."
                                              " If the laboratory is modified, it will be replace by "
                                              "the 'Default report template' present in the laboratory.")

    def do_cancel(self):
        res = super(LimsAnalysisRequest, self).do_cancel()
        self.mapped('analysis_report_ids').do_cancelled()
        return res

    def check_before_create_report(self):
        self.ensure_one()
        if 0 < self.nb_reports and not all([report.state == 'cancel' for report in self.analysis_report_ids]):
            return {
                'name': 'Confirmation',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'confirmation.create.report.request',
                'context': {'default_analysis_request_id': self.id},
                'target': 'new',
            }
        return self.create_report()

    def create_report(self):
        self.ensure_one()
        report_action = self.env['ir.actions.act_window']._for_xml_id('lims_report.create_report_wizard_action')
        report_action['context'] = {
            'default_analysis_request_id': self.id,
            'default_laboratory_id': self.labo_id.id,
            'default_report_template_id': self.report_template_id.id,
        }
        return report_action

    def open_reports(self):
        self.ensure_one()
        return {
            'name': 'Analysis Report',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.report',
            'view_mode': 'tree,form',
            'context': {'search_default_analysis_request_id': self.id, 'default_analysis_request_id': self.id},
        }

    def compute_is_ok_for_report(self):
        for record in self:
            record.is_ok_for_report = record.sample_ids.filtered(lambda s: s.analysis_id)

    def compute_nb_reports(self):
        for record in self:
            record.nb_reports = len(record.analysis_report_ids)

    @api.onchange('labo_id')
    def get_report_template_id(self):
        """
        Get the default report model define in laboratory
        :return:
        """
        for record in self:
            record.report_template_id = record.labo_id.default_report_template

    def check_done_state(self):
        res = super(LimsAnalysisRequest, self).check_done_state()
        report_line_obj = self.env['lims.analysis.report.line']
        for record in self:
            report_line_ids = report_line_obj.search([('analysis_id', 'in', record.analysis_ids.ids)])
            analysis_ids = record.analysis_ids.filtered(lambda a: a.rel_type != 'cancel')
            all_analysis_in_report = all([analysis.id in report_line_ids.mapped('analysis_id').ids for analysis in
                                          analysis_ids])
            if all_analysis_in_report and record.state == 'done' and all([r.state in ['sent', 'cancel'] for r
                                                                          in record.analysis_report_ids]):
                record.state = 'report'
        return res

    def get_sent_reports(self, get_only_if_one=False, report_state=False):
        self.ensure_one()
        if not report_state:
            report_state = 'sent'
        report_ids = self.analysis_report_ids.filtered(
            lambda r: r.state == report_state and r.kanban_state != 'blocked')
        if get_only_if_one:
            return report_ids if report_ids and len(report_ids) == 1 else False
        return report_ids
