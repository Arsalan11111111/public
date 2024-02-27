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
from odoo import fields, models, api, _


class LimsSamplingPoint(models.Model):
    _name = 'lims.sampling.point'
    _description = 'Sampling Point'
    _order = 'sequence'

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    tags_ids = fields.Many2many('lims.sampling.tag', 'rel_lims_sampling_tag',
                                'sampling_point_id', 'tag_id', string='Tags')
    description = fields.Text('Description')
    matrix_id = fields.Many2one('lims.matrix', 'Matrix')
    regulation_id = fields.Many2one('lims.regulation')
    partner_id = fields.Many2one('res.partner', 'Customer')
    quality_zone_id = fields.Many2one('lims.quality.zone', 'Quality Zone')
    field1 = fields.Char('Field 1')
    field2 = fields.Char('Field 2')
    field3 = fields.Boolean('Field 3')
    sampling_category_id = fields.Many2one('lims.sampling.category', 'Category Sampling')

    last_analysis_id = fields.Many2one('lims.analysis', compute='compute_last_analysis', store=True)
    date_last_analysis = fields.Datetime('Date Last Analysis', compute='compute_last_analysis', store=True)
    rel_status_last_analysis = fields.Selection(string='Status last analysis', related='last_analysis_id.state')
    analysis_ids = fields.One2many('lims.analysis', 'sampling_point_id', 'All Analysis')
    total_analysis = fields.Integer('Total Analysis', compute='count_analysis')
    total_result = fields.Integer('Total Results', compute='count_result')
    total_compute_result = fields.Integer('Total Compute Results', compute='count_compute_result')
    total_sel_result = fields.Integer('Total Sel Results', compute='count_sel_result')
    total_text_result = fields.Integer('Total Text Results', compute='count_text_result')
    location_id = fields.Many2one('lims.sampling.point.location', 'Location')
    sampling_type_id = fields.Many2one('lims.sampling.type', 'Sampling Type')
    partner_owner_id = fields.Many2one('res.partner', 'Partner Owner')

    def count_analysis(self):
        """
        Compute number of analysis
        :return:
        """
        for record in self:
            record.total_analysis = len(record.analysis_ids)

    def count_compute_result(self):
        """
        Compute number of compute result
        :return:
        """
        for record in self:
            record.total_compute_result = \
                self.env['lims.analysis.compute.result'].search_count([('analysis_id', 'in', record.analysis_ids.ids)])

    def count_sel_result(self):
        """
        Compute number of selection result
        :return:
        """
        for record in self:
            record.total_sel_result = \
                self.env['lims.analysis.sel.result'].search_count([('analysis_id', 'in', record.analysis_ids.ids)])

    def count_text_result(self):
        """
        Compute number of text result
        :return:
        """
        for record in self:
            record.total_text_result = \
                self.env['lims.analysis.text.result'].search_count([('analysis_id', 'in', record.analysis_ids.ids)])

    def count_result(self):
        """
        Compute number of result
        :return:
        """
        for record in self:
            record.total_result = self.env['lims.analysis.numeric.result'].search_count([
                ('analysis_id', 'in', record.analysis_ids.ids)
            ])

    @api.depends('analysis_ids', 'analysis_ids.date_done', 'analysis_ids.active')
    def compute_last_analysis(self):
        """
        Compute the last analysis for the sampling point and set it in the record (+ the date_done of the analysis)
        :return:
        """
        for sampling_point in self.filtered(lambda r: r.analysis_ids):
            analysis_ids = sampling_point.analysis_ids.filtered(
                lambda r: r.date_done and r.active and r.stage_id.type in ('done', 'validated1', 'validated2')
            )

            if analysis_ids:
                analysis_ids = analysis_ids.sorted(key=lambda r: r.date_done, reverse=True)
                sampling_point.last_analysis_id = analysis_ids[0]
                sampling_point.date_last_analysis = analysis_ids[0].date_done

    def get_all_analysis_view(self):
        """
        Open the view analysis where the sampling point is in
        :return:
        """
        return {
            'name': _('Analysis'),
            'domain': [('sampling_point_id', '=', self.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'context': {'default_sampling_point_id': self.id},
        }

    def get_all_analysis_result_view(self):
        """
        Open the view result where the sampling point is in
        :return:
        """
        return {
            'name': _('Result'),
            'domain': [('analysis_id', 'in', self.analysis_ids.ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def get_all_analysis_sel_result_view(self):
        """
        Open the view selection result where the sampling point is in
        :return:
        """
        return {
            'name': _('Sel Result'),
            'domain': [('analysis_id', 'in', self.analysis_ids.ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_text_result_view(self):
        """
        Open the view selection result where the sampling point is in
        :return:
        """
        return {
            'name': _('Text Result'),
            'domain': [('analysis_id', 'in', self.analysis_ids.ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_compute_result_view(self):
        """
        Open the view compute result where the sampling point is in
        :return:
        """
        return {
            'name': _('Compute Result'),
            'domain': [('analysis_id', 'in', self.analysis_ids.ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }
