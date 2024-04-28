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
from odoo import models, api, fields


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    task_id = fields.Many2one('project.task', 'Task', tracking=True, domain="[('rel_allow_lims_links','=',True)]")
    project_id = fields.Many2one('project.project', domain="[('allow_lims_links','=',True)]")
    allow_lims_project_ids = fields.Many2many('project.project', compute='get_all_allow_lims_project')

    def set_task_in_analysis(self):
        for record in self:
            record.analysis_ids.with_context(force_write=True).write({
                'task_id': record.task_id.id
            })

    def write(self, vals):
        res = super(LimsAnalysisRequest, self).write(vals)
        if vals.get('task_id') and not self.env.context.get('force_write'):
            self.set_task_in_analysis()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        requests = super().create(vals_list)
        for rec in requests:
            if rec.task_id:
                rec.set_task_in_analysis()
        return requests

    @api.depends('project_id')
    def get_all_allow_lims_project(self):
        allow_lims_projects = self.env['project.project'].search([('allow_lims_links', '=', True)])
        for record in self:
            record.allow_lims_project_ids = record.project_id if record.project_id else allow_lims_projects

    @api.onchange('task_id')
    def set_project_from_task_id(self):
        for record in self:
            if record.task_id and record.task_id.project_id != record.project_id:
                record.project_id = record.task_id.project_id

    def add_analysis_values(self, sample_id, sample_info=False):
        if not sample_info:
            sample_info = {}
        vals = super().add_analysis_values(sample_id, sample_info)
        vals.update({
            'task_id': self.task_id.id or False,
        })
        return vals
