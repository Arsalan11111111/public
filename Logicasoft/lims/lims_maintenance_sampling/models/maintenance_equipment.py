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


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    sampling_point_ids = fields.One2many('lims.sampling.point', 'equipment_id', 'Sampling points')
    total_sampling_point = fields.Integer(compute='compute_total_sampling_point')
    total_analysis = fields.Integer('Total Analysis', compute='count_analysis')
    total_result = fields.Integer('Total Results', compute='count_result')
    total_compute_result = fields.Integer('Total Compute Results', compute='count_compute_result')
    total_sel_result = fields.Integer('Total Sel Results', compute='count_sel_result')
    total_text_result = fields.Integer('Total Text Results', compute='count_text_result')

    def get_all_analysis_view(self):
        """
        Open the view analysis where the sampling point is in.
        :return: Analysis view.
        """
        return {
            'name': _('Analysis'),
            'domain': [('sampling_point_id', 'in', self.sampling_point_ids.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form,pivot,graph,calendar',
            'view_type': 'form',
        }

    def get_all_result_view(self):
        """
        Open the view result where the sampling point is in.
        :return: Analysis result view.
        """
        return {
            'name': _('Analysis Result'),
            'domain': [('analysis_id', 'in', self.sampling_point_ids.mapped('analysis_ids').ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_sel_result_view(self):
        """
        Open the view selection result where the sampling point is in.
        :return: Analysis select result view.
        """
        return {
            'name': _('Analysis Sel Result'),
            'domain': [('analysis_id', 'in', self.sampling_point_ids.mapped('analysis_ids').ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
            'view_type': 'form',
        }

    def get_all_compute_result_view(self):
        """
        Open the view compute result where the sampling point is in.
        :return: Analysis compute result view.
        """
        return {
            'name': _('Compute Analysis Result'),
            'domain': [('analysis_id', 'in', self.sampling_point_ids.mapped('analysis_ids').ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_text_result_view(self):
        return {
            'name': _('Text Analysis Result'),
            'domain': [('analysis_id', 'in', self.sampling_point_ids.mapped('analysis_ids').ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def count_analysis(self):
        """Compute number of analysis."""
        for record in self:
            record.total_analysis = sum(record.sampling_point_ids.mapped('total_analysis'))

    def count_compute_result(self):
        """Compute number of compute result."""
        for record in self:
            record.total_compute_result = sum(record.sampling_point_ids.mapped('total_compute_result'))

    def count_sel_result(self):
        """Compute number of selection result."""
        for record in self:
            record.total_sel_result = sum(record.sampling_point_ids.mapped('total_sel_result'))

    def count_result(self):
        """Compute number of result."""
        for record in self:
            record.total_result = sum(record.sampling_point_ids.mapped('total_result'))

    def count_text_result(self):
        """Compute number of result."""
        for record in self:
            record.total_text_result = sum(record.sampling_point_ids.mapped('total_text_result'))

    def open_view_sampling_point(self):
        """
        Open the sampling point view.
        :return: Sampling point view.
        """
        self.ensure_one()
        return {
            'name': _('Sampling Point'),
            'res_model': 'lims.sampling.point',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', self.sampling_point_ids.ids)],
            'context': {'default_equipment_id': self.id}
        }

    def compute_total_sampling_point(self):
        """Compute total of sampling point."""
        for record in self:
            record.total_sampling_point = len(record.sampling_point_ids)
