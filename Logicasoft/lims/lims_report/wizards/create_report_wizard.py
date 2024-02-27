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
from odoo import models, fields, api, exceptions, _, Command


class CreateReportWizard(models.TransientModel):
    _name = 'create.report.wizard'
    _description = 'Report Wizard'

    analysis_request_id = fields.Many2one('lims.analysis.request')
    laboratory_id = fields.Many2one('lims.laboratory', related='analysis_request_id.labo_id')
    version = fields.Integer()
    title = fields.Char()
    report_date = fields.Datetime(default=fields.Datetime.now)
    line_ids = fields.One2many('create.report.wizard.line', 'wizard_id', 'Analysis')
    report_template_id = fields.Many2one('lims.analysis.report.template')
    option_ids = fields.Many2many('ir.model.fields', domain=[('model_id', '=', 'lims.analysis.report'),
                                                             ('ttype', '=', 'boolean'),
                                                             ('name', '=like', 'option_%')])

    def create_report_analysis(self, analysis_ids):
        line_obj = self.env['create.report.wizard.line']
        report_action = self.env['ir.actions.act_window']._for_xml_id('lims_report.create_report_wizard_action')
        line = []
        for analysis in analysis_ids:
            vals = {'analysis_id': analysis.id}
            line.append(line_obj.create(vals).id)
        request_id = analysis_ids[0].request_id
        labo_id = analysis_ids[0].laboratory_id
        report_action['context'] = {
            'default_line_ids': line,
            'default_analysis_request_id': request_id.id,
            'default_laboratory_id': labo_id.id,
        }
        return report_action

    @api.onchange('analysis_request_id')
    def onchange_analysis_request_id(self):
        self.version = (len(self.analysis_request_id.analysis_report_ids) + 1)
        if not self.line_ids:
            self.populate_lines()

    def get_report_val(self):
        if not self.laboratory_id.seq_report_id:
            raise ValueError(_(f"Add a report sequence in the laboratory : ") % self.laboratory_id.name)
        vals = {
            'name': self.laboratory_id.seq_report_id.next_by_id(),
            'analysis_request_id': self.analysis_request_id.id,
            'laboratory_id': self.laboratory_id.id,
            'version': (len(self.analysis_request_id.analysis_report_ids) + 1),
            'title': self.title,
            'report_date': self.report_date,
            'partner_id': self.analysis_request_id.partner_id.id,
            'report_id': self.get_default_report(),
            'report_template_id': self.report_template_id.id,
            'partner_contact_ids': [
                Command.link(contact.id) for contact in self.analysis_request_id.partner_contact_ids],
        }
        if self.analysis_request_id.analysis_report_ids:
            vals['previous_analysis_report_id'] = self.analysis_request_id.analysis_report_ids.sorted(
                lambda p: p.create_date, reverse=True)[0].id
        if self.option_ids:
            vals.update(self.report_template_id.get_dict_for_selected_options(self.option_ids))
        return vals

    def create_report(self):
        if not self.laboratory_id.seq_report_id:
            raise exceptions.MissingError(_('You must define a sequence report for laboratory %s before creating a '
                                            'report') % self.laboratory_id.name)
        self.analysis_request_id.analysis_report_ids.write({'state': 'cancel'})
        report_obj = self.env['lims.analysis.report']
        report_line_obj = self.env['lims.analysis.report.line']
        report_vals = self.get_report_val()
        report_id = report_obj.create(report_vals)
        for line_id in self.line_ids:
            report_line_obj.create({
                'report_id': report_id.id,
                'analysis_id': line_id.analysis_id.id,
            })
        for follower in self.analysis_request_id.message_follower_ids:
            report_id.message_subscribe(partner_ids=follower.partner_id.ids, subtype_ids=follower.subtype_ids.ids)
        self.analysis_request_id.date_report = fields.Datetime.now()
        return self.analysis_request_id.open_reports()

    @api.model
    def populate_lines(self):
        line_obj = self.env['create.report.wizard.line']
        for sample_id in self.analysis_request_id.sample_ids.filtered(lambda s: s.analysis_id):
            line_obj.new({
                'wizard_id': self.id,
                'analysis_id': sample_id.analysis_id.id,
            })

    def get_default_report(self):
        """
        Set the default template report on the wizard, follow this rule.
        First check in request if report template is set.
        Second check in laboratory's request if report template is set.

        :return:
        """
        self.ensure_one()
        report_id = False
        if self.analysis_request_id and self.analysis_request_id.report_template_id:
            report_id = self.analysis_request_id.report_template_id.report_id.id
        elif self.laboratory_id and self.laboratory_id.default_report_template:
            report_id = self.laboratory_id.get_default_report_model_id().id
        return report_id

    @api.onchange('report_template_id')
    def onchange_report_template_id(self):
        self.option_ids = self.report_template_id.option_ids

class CreateReportWizardLines(models.TransientModel):
    _name = 'create.report.wizard.line'
    _description = 'Report Wizard Line'

    wizard_id = fields.Many2one('create.report.wizard')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis')
