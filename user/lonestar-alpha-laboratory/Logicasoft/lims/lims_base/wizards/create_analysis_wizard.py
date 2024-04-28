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
from odoo import models, fields, api, _
from datetime import datetime


class CreateAnalysis(models.TransientModel):
    _name = 'create.analysis.wizard'
    _description = 'Create Analysis'

    @api.model
    def create_line_ids(self):
        line_ids = self.env['create.analysis.wizard.line'].sudo()
        analysis_request = self.env['lims.analysis.request'].browse(self.env.context.get('default_analysis_request'))
        for sample_id in analysis_request.sample_ids:
            line_ids += line_ids.new({
                'due_date': sample_id.analysis_id.due_date if sample_id.analysis_id else fields.Datetime.today(),
                'date_plan': sample_id.analysis_id.date_plan if sample_id.analysis_id else fields.Datetime.today(),
                'category_id': sample_id.analysis_id.category_id.id if sample_id.analysis_id else
                analysis_request.labo_id.default_analysis_category_id.id,
                'sample_id': sample_id,
                'sample_name': sample_id.name,
                'partner_contact_ids': [(4, contact.id) for contact in analysis_request.partner_contact_ids]
                if analysis_request.partner_contact_ids else False,
                'analysis_id': sample_id.analysis_id.id if sample_id.analysis_id else False,
            })
        return line_ids

    def get_default_laboratory(self):
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    def get_default_customer_contact(self):
        analysis_request = self.env['lims.analysis.request'].browse(self.env.context.get('default_analysis_request'))
        return analysis_request.partner_contact_ids

    def get_domain_customer_contact(self):
        analysis_request = self.env['lims.analysis.request'].browse(self.env.context.get('default_analysis_request'))
        return [('parent_id', '=', analysis_request.partner_id.id)]

    def get_default_request_category(self):
        default_laboratory_id = self.get_default_laboratory()
        return default_laboratory_id.default_analysis_category_id.id

    receipt_date = fields.Datetime('Date of receipt', default=fields.Datetime.now)
    analysis_request = fields.Many2one('lims.analysis.request')
    analysis_request_type_id = fields.Many2one(related='analysis_request.request_type_id', string='Request Type')
    line_ids = fields.One2many('create.analysis.wizard.line', 'wizard_id', default=create_line_ids)
    due_date = fields.Datetime('Due Date', default=fields.Datetime.now)
    date_plan = fields.Datetime('Date plan', default=fields.Datetime.now)
    date_sample = fields.Datetime('Date sample', default=fields.Datetime.now)
    category_id = fields.Many2one('lims.analysis.category', default=get_default_request_category)
    partner_contact_ids = fields.Many2many('res.partner', default=get_default_customer_contact,
                                           domain=get_domain_customer_contact)
    note = fields.Text('Internal comment',
                       help="Additional comment addressed to the internal team (won't be printed on analysis report)")
    reception_deviation = fields.Boolean('Reception Deviation(s)')

    @api.onchange('analysis_request')
    def onchange_analysis_request(self):
        self.category_id = self.analysis_request.labo_id.default_analysis_category_id

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            self.line_ids.update({
                'category_id': self.category_id.id
            })

    @api.onchange('due_date')
    def onchange_due_date(self):
        if self.due_date:
            self.line_ids.update({
                'due_date': self.due_date
            })

    @api.onchange('date_plan')
    def onchange_date_plan(self):
        if self.date_plan:
            self.line_ids.update({
                'date_plan': self.date_plan
            })

    @api.onchange('date_sample')
    def onchange_date_sample(self):
        if self.date_sample:
            self.line_ids.update({
                'date_sample': self.date_sample
            })

    @api.onchange('partner_contact_ids')
    def onchange_partner_contact_ids(self):
        if self.partner_contact_ids:
            self.line_ids.update({
                'partner_contact_ids': self.partner_contact_ids
            })

    @api.onchange('note')
    def onchange_note(self):
        self.line_ids.update({
            'note': self.note
        })

    @api.onchange('reception_deviation')
    def onchange_reception_deviation(self):
        self.line_ids.update({
            'reception_deviation': self.reception_deviation
        })

    def create_analysis(self):
        self.ensure_one()
        sample_and_due_date = {}
        for line in self.sudo().line_ids:
            sample_and_due_date[line.sample_id.id] = line.get_vals_for_sample()
            line.sample_id.name = line.sample_name
        sample_ids = (self.line_ids and self.line_ids.sample_id) or None
        analysis_ids = self.analysis_request.sudo().create_analysis(self.receipt_date, sample_and_due_date,
                                                                    sample_ids=sample_ids)
        self.analysis_request.warning_update_analysis = False
        return analysis_ids


class AnalysisMassChangeWizardLine(models.TransientModel):
    _name = 'create.analysis.wizard.line'
    _description = 'Create Analysis Line'

    wizard_id = fields.Many2one('create.analysis.wizard')
    due_date = fields.Datetime()
    sample_id = fields.Many2one('lims.analysis.request.sample')
    sample_name = fields.Char()
    date_plan = fields.Datetime('Date plan')
    date_sample = fields.Datetime('Date sample')
    category_id = fields.Many2one('lims.analysis.category')
    partner_contact_ids = fields.Many2many('res.partner')
    analysis_id = fields.Many2one('lims.analysis')
    note = fields.Text('External comment',
                          help='Additional comment addressed to the customer (will be printed on analysis report)')
    reception_deviation = fields.Boolean('Reception Deviation(s)')

    def get_vals_for_sample(self):
        self.ensure_one()
        sample_vals = {
            'due_date': self.due_date,
            'date_plan': self.date_plan,
            'date_sample': self.date_sample,
            'category_id': self.category_id.id,
            'partner_contact_ids': self.partner_contact_ids.ids,
            'note': self.note,
            'reception_deviation': self.reception_deviation,
        }
        return sample_vals
