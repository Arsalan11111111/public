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


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    tour_id = fields.Many2one('lims.tour', 'Tour', store=True, tracking=True)
    rel_tour_id_state = fields.Selection(related='tour_id.state', string='State tour', store=True, readonly=True)
    date_tour = fields.Datetime('Date Tour', related='tour_id.date', store=True)
    is_on_site_complete = fields.Boolean(compute='compute_on_site_complete', store=True, copy=False,
                                         string='Complet on site')

    def do_wip(self, wip_stage_id=False):
        """
        Pass the analysis in stage "WIP"
        :return:
        """
        analysis_ids = self
        if self.env.context.get('update_from_tour_line'):
            analysis_ids = self.filtered(lambda a: a.rel_type != 'todo')
        return super(LimsAnalysis, analysis_ids).do_wip(wip_stage_id)

    def copy(self, default=None):
        self.ensure_one()
        res = super().copy(default)
        if res.tour_id:
            self.env['lims.tour.line'].create({
                'tour_id': self.tour_id.id,
                'analysis_id': res.id,
                'sampler_id': res.sampler_id and res.sampler_id.id or False,
                })
        return res

    def get_vals_for_recurrence_tour(self):
        """
        Needed to overload the function for customer, change the duplication vals for duplication form lims_tour
        :return:
        """
        return self.get_vals_for_recurrence()

    @api.depends('tour_id',
                 'result_num_ids', 'result_num_ids.rel_type',
                 'result_sel_ids', 'result_sel_ids.rel_type',
                 'result_compute_ids', 'result_compute_ids.rel_type',
                 'result_text_ids', 'result_text_ids.rel_type')
    def compute_on_site_complete(self):
        """
        Sampler need to see easily that a sample is full done on site's results.
        :return:
        """
        for record in self:
            results = record.get_results_filtered(
                domain=lambda r: r.rel_is_on_site and r.rel_type in ['draft', 'plan', 'todo', 'wip'])
            record.is_on_site_complete = not bool(results)
