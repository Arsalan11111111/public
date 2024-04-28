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


class AnalysisMassChangeWizard(models.TransientModel):
    _name = 'analysis.mass.change.wizard'
    _description = 'Analysis Mass Change'

    line_ids = fields.One2many('analysis.mass.change.wizard.line', 'wizard_id')
    stage_id = fields.Many2one('lims.analysis.stage', 'Stage', domain=[('type', 'in', ['plan', 'todo', 'cancel'])])
    rel_type = fields.Selection(related='stage_id.type', readonly=True)
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler', domain=[('is_sampler', '=', True)])
    external_sampling = fields.Boolean('External Sampling')
    date_sample = fields.Datetime('Date sample')
    date_sample_receipt = fields.Datetime('Date Sample Receipt')
    assigned_to = fields.Many2one('res.users', 'Assigned to')
    date_plan = fields.Datetime('Date plan')
    regulation_id = fields.Many2one('lims.regulation', 'Regulation')
    cancel_reason = fields.Char()
    category_id = fields.Many2one('lims.analysis.category', 'Category')
    note = fields.Char('Note')
    date_sample_begin = fields.Datetime('Date Sample begin')

    first_edit_date_sample = fields.Boolean()
    first_edit_date_sample_receipt = fields.Boolean()
    first_edit_sampler = fields.Boolean()
    first_edit_external_sampling = fields.Boolean()
    first_edit_assigned_to = fields.Boolean()
    first_edit_date_plan = fields.Boolean()
    first_edit_date_sample_begin = fields.Boolean()
    first_edit_regulation = fields.Boolean()
    first_edit_cancel_reason = fields.Boolean()
    first_edit_category = fields.Boolean()
    first_edit_note = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        """
        Generate line_ids from context.active_ids
        :param fields_list:
        :return:
        """
        res = super(AnalysisMassChangeWizard, self).default_get(fields_list)
        line_ids = []
        for analysis in self.env.context.get('active_ids', []):
            analysis_id = self.env['lims.analysis'].browse(analysis)
            line_ids.append((0, 0,
                             {
                                 'analysis_id': analysis_id.id,
                                 'stage_id': analysis_id.stage_id.id,
                                 'sampler_id': analysis_id.sampler_id.id,
                                 'external_sampling': analysis_id.external_sampling,
                                 'date_sample': analysis_id.date_sample,
                                 'date_sample_receipt': analysis_id.date_sample_receipt,
                                 'assigned_to': analysis_id.assigned_to.id,
                                 'cancel_reason': analysis_id.cancel_reason,
                                 'date_plan': analysis_id.date_plan,
                                 'category_id': analysis_id.category_id.id,
                                 'regulation_id': analysis_id.regulation_id.id,
                                 'note': analysis_id.note,
                                 'date_sample_begin': analysis_id.date_sample_begin
                             }))
        res.update({'line_ids': line_ids})
        return res

    @api.onchange('note')
    def onchange_note(self):
        if self.first_edit_note:
            self.line_ids.update({'note': self.note})
        else:
            self.update({'first_edit_note': True})

    @api.onchange('stage_id')
    def onchange_state(self):
        if self.stage_id:
            self.line_ids.update({'stage_id': self.stage_id.id})
            if self.stage_id.type == 'todo':
                self.line_ids.update({'date_sample_receipt': fields.Datetime.now()})

    @api.onchange('assigned_to')
    def onchange_assigned_to(self):
        if self.first_edit_assigned_to:
            self.line_ids.update({'assigned_to': self.assigned_to.id})
        else:
            self.update({'first_edit_assigned_to': True})

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.first_edit_category:
            self.line_ids.update({'category_id': self.category_id.id})
        else:
            self.update({'first_edit_category': True})

    @api.onchange('regulation_id')
    def onchange_regulation_id(self):
        if self.first_edit_regulation:
            self.line_ids.update({'regulation_id': self.regulation_id.id})
        else:
            self.update({'first_edit_regulation': True})

    @api.onchange('sampler_id')
    def onchange_sampler_id(self):
        if self.first_edit_sampler:
            self.line_ids.update({'sampler_id': self.sampler_id.id})
        else:
            self.update({'first_edit_sampler': True})

    @api.onchange('external_sampling')
    def onchange_external_sampling(self):
        if self.first_edit_external_sampling:
            self.line_ids.update({'external_sampling': self.external_sampling})
        else:
            self.update({'first_edit_external_sampling': True})

    @api.onchange('date_sample')
    def onchange_date_sample(self):
        if self.first_edit_date_sample:
            self.line_ids.update({'date_sample': self.date_sample})
        else:
            self.update({'first_edit_date_sample': True})

    @api.onchange('date_plan')
    def onchange_date_plan(self):
        if self.first_edit_date_plan:
            self.line_ids.update({'date_plan': self.date_plan})
        else:
            self.update({'first_edit_date_plan': True})

    @api.onchange('date_sample_begin')
    def onchange_date_sample_begin(self):
        if self.first_edit_date_sample_begin:
            self.line_ids.update({'date_sample_begin': self.date_sample_begin})
        else:
            self.update({'first_edit_date_sample_begin': True})

    @api.onchange('date_sample_receipt')
    def onchange_date_sample_receipt(self):
        if self.first_edit_date_sample_receipt:
            self.line_ids.update({'date_sample_receipt': self.date_sample_receipt})
        else:
            self.update({'first_edit_date_sample_receipt': True})

    @api.onchange('cancel_reason')
    def onchange_cancel_reason(self):
        if self.first_edit_cancel_reason:
            self.line_ids.update({'cancel_reason': self.cancel_reason})
        else:
            self.update({'first_edit_cancel_reason': True})

    def save_analysis(self):
        sampler_ids = self.line_ids.mapped('sampler_id')
        for sampler_id in sampler_ids:
            self.line_ids.filtered(lambda l: l.sampler_id == sampler_id).mapped('analysis_id').write({
                'sampler_id': sampler_id.id
            })
        values = self.line_ids.mapped('external_sampling')
        for value in values:
            if value:
                self.line_ids.filtered(lambda l: l.external_sampling == value).mapped('analysis_id').write({
                    'sampler_id': False,
                })
            self.line_ids.filtered(lambda l: l.external_sampling == value).mapped('analysis_id').write({
                'external_sampling': value,
            })
        values = self.line_ids.mapped('date_sample')
        for value in values:
            self.line_ids.filtered(lambda l: l.date_sample == value).mapped('analysis_id').write({
                'date_sample': value
            })
        values = self.line_ids.mapped('date_sample_receipt')
        for value in values:
            self.line_ids.filtered(lambda l: l.date_sample_receipt == value).mapped('analysis_id').write({
                'date_sample_receipt': value
            })
        values = self.line_ids.mapped('assigned_to')
        for user in values:
            self.line_ids.filtered(lambda l: l.assigned_to == user).mapped('analysis_id').write({
                'assigned_to': user.id
            })
        values = self.line_ids.mapped('date_sample_begin')
        for value in values:
            self.line_ids.filtered(lambda l: l.date_sample_begin == value).mapped('analysis_id').write({
                'date_sample_begin': value
            })
        stage_ids = self.line_ids.mapped('stage_id')
        for stage_id in stage_ids:
            analysis_ids = self.line_ids.filtered(lambda l: l.stage_id == stage_id).mapped('analysis_id'). \
                filtered(lambda a: a.stage_id != stage_id)
            if stage_id.type == 'plan':
                analysis_ids.filtered(lambda a: a.stage_id.type == 'draft').do_plan()
            elif stage_id.type == 'todo':
                if analysis_ids.filtered(lambda a: a.stage_id.type == 'draft'):
                    analysis_ids.filtered(lambda a: a.stage_id.type == 'draft').do_plan()
                analysis_ids.filtered(lambda a: a.stage_id.type == 'plan').do_todo()
            elif stage_id.type == 'validated2':
                if not self.user_has_groups('lims_base.validator2_group'):
                    raise exceptions.AccessError(_('You must have extra rights to validate an analysis.'))
                analysis_ids.do_validation2()
            elif stage_id.type == 'cancel':
                for analysis in analysis_ids:
                    analysis.do_cancel(self.line_ids.filtered(lambda l: l.analysis_id == analysis).cancel_reason)
        values = self.line_ids.mapped('date_plan')
        for value in values:
            self.line_ids.filtered(lambda l: l.date_plan == value).mapped('analysis_id').write({
                'date_plan': value
            })
        category_ids = self.line_ids.mapped('category_id')
        for category_id in category_ids:
            self.line_ids.filtered(lambda l: l.category_id == category_id).mapped('analysis_id').write({
                'category_id': category_id.id
            })
        regulation_ids = self.line_ids.mapped('regulation_id')
        for regulation_id in regulation_ids:
            self.line_ids.filtered(lambda l: l.regulation_id == regulation_id).mapped('analysis_id').write({
                'regulation_id': regulation_id.id
            })
        for line in self.line_ids.filtered(lambda l: l.note):
            line.analysis_id.note = line.note


class AnalysisMassChangeWizardLine(models.TransientModel):
    _name = 'analysis.mass.change.wizard.line'
    _description = 'Analysis Mass Change Line'

    wizard_id = fields.Many2one('analysis.mass.change.wizard')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis')
    stage_id = fields.Many2one('lims.analysis.stage', 'Stage', domain=[('type', 'in', ['plan', 'todo', 'cancel'])])
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler', domain=[('is_sampler', '=', True)])
    external_sampling = fields.Boolean('External Sampling')
    date_sample = fields.Datetime('Date sample')
    date_sample_receipt = fields.Datetime('Date Sample Receipt')
    assigned_to = fields.Many2one('res.users', 'Assigned to')
    cancel_reason = fields.Char()
    date_plan = fields.Datetime('Date plan')
    category_id = fields.Many2one('lims.analysis.category', 'Category')
    regulation_id = fields.Many2one('lims.regulation', 'Regulation')
    rel_type = fields.Selection(related='stage_id.type', readonly=True)
    note = fields.Char('Note')
    date_sample_begin = fields.Datetime('Date Sample begin')
