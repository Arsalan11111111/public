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


class ProjectProject(models.Model):
    _inherit = 'project.project'

    nb_request = fields.Integer(compute='compute_nb_request_nb_analysis_all_result', string='Requests')
    nb_analysis = fields.Integer(compute='compute_nb_request_nb_analysis_all_result', string='Analysis')
    nb_numeric_result = fields.Integer('Numeric Results', compute='compute_nb_request_nb_analysis_all_result')
    nb_compute_result = fields.Integer('Compute Results', compute='compute_nb_request_nb_analysis_all_result')
    nb_sel_result = fields.Integer('Sel Results', compute='compute_nb_request_nb_analysis_all_result')
    nb_text_result = fields.Integer('Text Results', compute='compute_nb_request_nb_analysis_all_result')
    allow_lims_links = fields.Boolean(string='Lims Project', tracking=True,
                                      help="This project will be able to link analyses and requests for analyses on "
                                           "the tasks of this project")
    is_lims_links = fields.Boolean('Is LIMS project', related='allow_lims_links')

    @api.depends('task_ids')
    def compute_nb_request_nb_analysis_all_result(self):
        for record in self:
            nb_analysis = False
            nb_request = False
            nb_numeric_result = False
            nb_compute_result = False
            nb_sel_result = False
            nb_text_result = False
            if record.allow_lims_links:
                nb_analysis = record.env['lims.analysis'].search_count([('rel_project_id', '=', record.id)])
                nb_request = record.env['lims.analysis.request'].search_count([('project_id', '=', record.id)])
                nb_numeric_result = record.env['lims.analysis.numeric.result'].search_count(
                    [('rel_project_id', '=', record.id)])
                nb_compute_result = record.env['lims.analysis.compute.result'].search_count(
                    [('rel_project_id', '=', record.id)])
                nb_sel_result = record.env['lims.analysis.sel.result'].search_count(
                    [('rel_project_id', '=', record.id)])
                nb_text_result = record.env['lims.analysis.text.result'].search_count(
                    [('rel_project_id', '=', record.id)])
            record.update({
                'nb_analysis': nb_analysis,
                'nb_request': nb_request,
                'nb_numeric_result': nb_numeric_result,
                'nb_compute_result': nb_compute_result,
                'nb_sel_result': nb_sel_result,
                'nb_text_result': nb_text_result,
            })


    def open_numeric_result(self):
        self.ensure_one()
        return {
            'name': _('Numeric Results'),
            'domain': [('rel_project_id', '=', self.id)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_compute_result(self):
        self.ensure_one()
        return {
            'name': _('Compute Results'),
            'domain': [('rel_project_id', '=', self.id)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_sel_result(self):
        self.ensure_one()
        return {
            'name': _('Sel Results'),
            'domain': [('rel_project_id', '=', self.id)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def open_text_result(self):
        self.ensure_one()
        return {
            'name': _('Text Results'),
            'domain': [('rel_project_id', '=', self.id)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def open_analysis(self):
        self.ensure_one()
        return {
            'name': _('Analysis'),
            'domain': [('rel_project_id', '=', self.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
        }

    def open_request(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'default_default_project_id': self.id,
        })
        return {
            'name': _('Analysis Request'),
            'domain': [('project_id', '=', self.id)],
            'res_model': 'lims.analysis.request',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'context': context,
        }
