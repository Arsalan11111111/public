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


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    task_id = fields.Many2one('project.task', 'Task', tracking=True, domain="[('rel_allow_lims_links','=',True)]")
    rel_project_id = fields.Many2one('project.project', related='task_id.project_id', store=True)

    def set_task_in_analysis_request(self):
        for record in self.filtered(lambda a: a.task_id and a.request_id):
            record.request_id.with_context(force_write=True).write({
                'task_id': record.task_id.id
            })

    def write(self, vals):
        res = super(LimsAnalysis, self).write(vals)
        if vals.get('task_id') and not self.env.context.get('force_write'):
            self.set_task_in_analysis_request()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        analysis = super().create(vals_list)
        for rec in analysis:
            if rec.task_id:
                rec.set_task_in_analysis_request()
        return analysis
