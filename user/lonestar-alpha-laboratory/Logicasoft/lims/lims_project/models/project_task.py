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
from odoo import models, api, exceptions, _, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    nb_analysis = fields.Integer('Nb Analysis', compute='compute_nb_analysis')
    nb_request = fields.Integer('Nb Request', compute='compute_nb_request_analysis')
    nb_numeric_result = fields.Integer('Numeric Results', compute='compute_nb_numeric_result')
    nb_compute_result = fields.Integer('Compute Results', compute='compute_nb_compute_result')
    nb_sel_result = fields.Integer('Sel Results', compute='compute_nb_sel_result')
    nb_text_result = fields.Integer('Text Results', compute='compute_nb_text_result')
    rel_allow_lims_links = fields.Boolean(related='project_id.allow_lims_links', store=True)

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = record.env['lims.analysis'].search_count(
                [('task_id', '=', record.id)])

    def compute_nb_request_analysis(self):
        for record in self:
            record.nb_request = record.env['lims.analysis.request'].search_count(
                [('task_id', '=', record.id)])

    def compute_nb_numeric_result(self):
        for record in self:
            record.nb_numeric_result = record.env['lims.analysis.numeric.result'].search_count(
                [('analysis_id.task_id', '=', record.id)])

    def compute_nb_compute_result(self):
        for record in self:
            record.nb_compute_result = record.env['lims.analysis.compute.result'].search_count(
                [('analysis_id.task_id', '=', record.id)])

    def compute_nb_sel_result(self):
        for record in self:
            record.nb_sel_result = record.env['lims.analysis.sel.result'].search_count(
                [('analysis_id.task_id', '=', record.id)])

    def compute_nb_text_result(self):
        for record in self:
            record.nb_text_result = record.env['lims.analysis.text.result'].search_count(
                [('analysis_id.task_id', '=', record.id)])

    def open_numeric_result(self):
        self.ensure_one()
        return {
            'name': _('Numeric Results'),
            'domain': [('rel_task_id', '=', self.id)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_compute_result(self):
        self.ensure_one()
        return {
            'name': _('Compute Results'),
            'domain': [('rel_task_id', '=', self.id)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_sel_result(self):
        self.ensure_one()
        return {
            'name': _('Sel Results'),
            'domain': [('rel_task_id', '=', self.id)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def open_text_result(self):
        self.ensure_one()
        return {
            'name': _('Text Results'),
            'domain': [('rel_task_id', '=', self.id)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_analysis(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'default_task_id': self.id,
        })
        return {
            'name': _('Analysis'),
            'domain': ['|', ('task_id', '=', self.id), ('request_id.task_id', '=', self.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'context': context,
        }

    def open_request_analysis(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'default_task_id': self.id,
        })
        return {
            'name': _('Analysis'),
            'domain': [('task_id', '=', self.id)],
            'res_model': 'lims.analysis.request',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'context': context,
        }
