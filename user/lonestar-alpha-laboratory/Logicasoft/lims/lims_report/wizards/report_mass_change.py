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
from odoo import models, fields, api, _, exceptions


class ReportMassChangeWizard(models.TransientModel):
    _name = 'report.mass.change.wizard'
    _description = 'Report Mass Change'

    line_ids = fields.One2many('report.mass.change.wizard.line', 'wizard_id')
    partner_id = fields.Many2one('res.partner', 'Partner')
    title = fields.Char('Title')
    customer_ref = fields.Char('Customer Ref.')
    comment = fields.Text('Comment')

    @api.model
    def default_get(self, fields_list):
        """
        Generate line_ids from context.active_ids
        :param fields_list:
        :return:
        """
        res = super(ReportMassChangeWizard, self).default_get(fields_list)
        line_ids = []
        for report in self.env.context.get('active_ids', []):
            report_id = self.env['lims.analysis.report'].browse(report)
            line_ids.append((0, 0,
                             {
                                 'report_id': report_id.id,
                                 'partner_id': report_id.partner_id.id,
                                 'title': report_id.title,
                                 'customer_ref': report_id.customer_ref,
                                 'comment': report_id.external_comment
                             }))
        res.update({'line_ids': line_ids})
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.line_ids.update({'partner_id': self.partner_id.id})

    @api.onchange('title')
    def onchange_title(self):
        if self.title:
            self.line_ids.update({'title': self.title})

    @api.onchange('customer_ref')
    def onchange_customer_ref(self):
        if self.customer_ref:
            self.line_ids.update({'customer_ref': self.customer_ref})

    @api.onchange('comment')
    def onchange_comment(self):
        if self.comment:
            self.line_ids.update({'comment': self.comment})

    def save_report(self):
        partner_ids = self.line_ids.mapped('partner_id')
        for partner_id in partner_ids:
            self.line_ids.filtered(lambda l: l.partner_id == partner_id).mapped('report_id').write({
                'partner_id': partner_id.id
            })
        for line_id in self.line_ids.filtered(lambda l: l.title):
            line_id.report_id.title = line_id.title
        for line_id in self.line_ids.filtered(lambda l: l.customer_ref):
            line_id.report_id.customer_ref = line_id.customer_ref
        for line_id in self.line_ids.filtered(lambda l: l.comment):
            line_id.report_id.external_comment = line_id.comment


class AnalysisMassChangeWizardLine(models.TransientModel):
    _name = 'report.mass.change.wizard.line'
    _description = 'Report Mass Change Line'

    wizard_id = fields.Many2one('report.mass.change.wizard')
    report_id = fields.Many2one('lims.analysis.report', 'Report')
    partner_id = fields.Many2one('res.partner', 'Partner')
    title = fields.Char('Title')
    customer_ref = fields.Char('Customer Ref.')
    comment = fields.Text('Comment')
