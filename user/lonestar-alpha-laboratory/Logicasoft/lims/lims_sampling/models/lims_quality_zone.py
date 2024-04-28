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
from odoo import fields, models, api, exceptions, _


class LimsQualityZone(models.Model):
    _name = 'lims.quality.zone'
    _description = 'Quality Zone'
    _order = 'sequence'

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    parent_id = fields.Many2one('lims.quality.zone', 'Parent')
    code = fields.Char('Code')
    entity_id = fields.Many2one('res.partner', 'Entity')
    description = fields.Text('Description')
    sampling_point_ids = fields.One2many('lims.sampling.point', 'quality_zone_id', 'Sampling Point', readonly=True)
    total_analysis = fields.Integer('Total Analysis', compute='count_analysis')
    total_result = fields.Integer('Total Results', compute='count_result')
    total_compute_result = fields.Integer('Total Compute Results', compute='count_compute_result')
    total_sel_result = fields.Integer('Total Sel Results', compute='count_sel_result')
    total_text_result = fields.Integer('Total Text Results', compute='count_text_result')

    def count_analysis(self):
        """
        Compute the number of analysis where quality zone is in
        :return:
        """
        for record in self:
            record.total_analysis = sum(sampling_point_id.total_analysis for sampling_point_id in record.sampling_point_ids)

    def count_compute_result(self):
        """
        Compute the number of compute result where quality zone is in
        :return:
        """
        for record in self:
            record.total_compute_result = sum(sampling_point_id.total_compute_result for sampling_point_id in record.sampling_point_ids)

    def count_sel_result(self):
        """
            Compute the number of selection result where quality zone is in
            :return:
            """
        for record in self:
            record.total_sel_result = sum(sampling_point_id.total_sel_result for sampling_point_id in record.sampling_point_ids)

    def count_result(self):
        """
        Compute the number of result where quality zone is in
        :return:
        """
        for record in self:
            record.total_result = sum(sampling_point_id.total_result for sampling_point_id in record.sampling_point_ids)

    def count_text_result(self):
        """
            Compute the number of text result where quality zone is in
            :return:
            """
        for record in self:
            record.total_text_result = sum(
                sampling_point_id.total_text_result for sampling_point_id in record.sampling_point_ids)

    def get_all_analysis_view(self):
        """
        Open the view on analysis where the quality zone is in
        :return:
        """
        return {
            'name': _('Analysis'),
            'domain': [('sampling_point_id', 'in', self.sampling_point_ids.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,pivot,graph,calendar',
        }

    def get_all_analysis(self):
        """
        Return all analysis where quality zone is in
        :return:
        """
        return self.env['lims.analysis'].search([('sampling_point_id', 'in', self.sampling_point_ids.ids)])

    def get_all_analysis_result_view(self):
        """
        Open the view result where quality zone is in
        :return:
        """
        return {
            'name': _('Result'),
            'domain': [('analysis_id', 'in', self.get_all_analysis().ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def get_all_analysis_sel_result_view(self):
        """
            Open the view sel result where quality zone is in
            :return:
            """
        return {
            'name': _('Selection Result'),
            'domain': [('analysis_id', 'in', self.get_all_analysis().ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_text_result_view(self):
        """
            Open the view text result where quality zone is in
            :return:
            """
        return {
            'name': _('Text Result'),
            'domain': [('analysis_id', 'in', self.get_all_analysis().ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_compute_result_view(self):
        """
            Open the view compute result where quality zone is in
            :return:
            """
        return {
            'name': _(' Compute Result'),
            'domain': [('analysis_id', 'in', self.get_all_analysis().ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }
