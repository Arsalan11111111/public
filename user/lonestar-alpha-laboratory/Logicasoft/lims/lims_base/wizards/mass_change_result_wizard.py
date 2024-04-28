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
from odoo import models, fields, api, exceptions, _


class MassChangeResultWizard(models.TransientModel):
    _name = 'mass.change.result.wizard'
    _description = 'Mass Change Result'

    analysis_result_ids = fields.Many2many('lims.analysis.numeric.result')
    analysis_sel_result_ids = fields.Many2many('lims.analysis.sel.result')
    analysis_compute_result_ids = fields.Many2many('lims.analysis.compute.result')
    analysis_text_result_ids = fields.Many2many('lims.analysis.text.result')
    nb_analysis_result_ids = fields.Integer(compute='compute_nb_analysis_result_ids')
    nb_analysis_sel_result_ids = fields.Integer(compute='compute_nb_analysis_sel_result_ids')
    nb_analysis_compute_result_ids = fields.Integer(compute='compute_nb_analysis_compute_result_ids')
    nb_analysis_text_result_ids = fields.Integer(compute='compute_nb_analysis_text_result_ids')

    @api.depends('analysis_text_result_ids')
    def compute_nb_analysis_text_result_ids(self):
        for record in self:
            record.nb_analysis_text_result_ids = len(record.analysis_text_result_ids)

    @api.depends('analysis_compute_result_ids')
    def compute_nb_analysis_compute_result_ids(self):
        for record in self:
            record.nb_analysis_compute_result_ids = len(record.analysis_compute_result_ids)

    @api.depends('analysis_sel_result_ids')
    def compute_nb_analysis_sel_result_ids(self):
        for record in self:
            record.nb_analysis_sel_result_ids = len(record.analysis_sel_result_ids)

    @api.depends('analysis_result_ids')
    def compute_nb_analysis_result_ids(self):
        for record in self:
            record.nb_analysis_result_ids = len(record.analysis_result_ids)

    def do_validate(self):
        self.ensure_one()
        if not self.user_has_groups('lims_base.validator1_group'):
            raise exceptions.AccessError(_('You must have extra rights to validate'))
        if self.analysis_result_ids:
            self.analysis_result_ids.filtered(lambda r: r.stage_id.type == 'done').do_validated()
        if self.analysis_sel_result_ids:
            self.analysis_sel_result_ids.filtered(lambda r: r.stage_id.type == 'done').do_validated()
        if self.analysis_compute_result_ids:
            self.analysis_compute_result_ids.filtered(lambda r: r.stage_id.type == 'done').do_validated()
        if self.analysis_text_result_ids:
            self.analysis_text_result_ids.filtered(lambda r: r.stage_id.type == 'done').do_validated()

    def do_second_validate(self):
        self.ensure_one()
        if not self.user_has_groups('lims_base.validator2_group'):
            raise exceptions.AccessError(_('You must have extra rights to validate'))
        analysis = self.env['lims.analysis']
        if self.analysis_result_ids:
            analysis += self.analysis_result_ids.mapped('sop_id').mapped('analysis_id')
        if self.analysis_sel_result_ids:
            analysis += self.analysis_sel_result_ids.mapped('sop_id').mapped('analysis_id')
        if self.analysis_compute_result_ids:
            analysis += self.analysis_compute_result_ids.mapped('sop_id').mapped('analysis_id')
        if self.analysis_text_result_ids:
            analysis += self.analysis_text_result_ids.mapped('sop_id').mapped('analysis_id')
        analysis = analysis.filtered(lambda a: a.stage_id.type == 'validated1')
        if not analysis:
            raise exceptions.ValidationError(_('Impossible to validate as some parameters are not in the selection'))
        analysis.do_validation2()

    def do_rework(self):
        self.ensure_one()
        if self.analysis_result_ids:
            self.analysis_result_ids.filtered(lambda r: r.stage_id.type in ['done', 'validated']).do_rework()
        if self.analysis_sel_result_ids:
            self.analysis_sel_result_ids.filtered(lambda r: r.stage_id.type in ['done', 'validated']).do_rework()
        if self.analysis_text_result_ids:
            self.analysis_text_result_ids.filtered(lambda r: r.stage_id.type in ['done', 'validated']).do_rework()

    def do_cancel(self):
        model = False
        ids = False
        if self.analysis_result_ids:
            model = 'default_result_ids'
            ids = self.analysis_result_ids.ids
        if self.analysis_sel_result_ids:
            model = 'default_result_sel_ids'
            ids = self.analysis_sel_result_ids.ids
        if self.analysis_compute_result_ids:
            model = 'default_result_compute_ids'
            ids = self.analysis_compute_result_ids.ids
        if self.analysis_text_result_ids:
            model = 'default_analysis_text_result_ids'
            ids = self.analysis_text_result_ids.ids
        if not model and not ids:
            raise exceptions.ValidationError(_('No valid data'))
        return {
            'name': 'Cancel result',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'result.cancel.wizard',
            'context': {model: ids},
            'target': 'new',
        }
