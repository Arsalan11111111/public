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


class LimsNetwork(models.Model):
    _name = 'lims.network'
    _description = 'Lims Network'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    entity_id = fields.Many2one('res.partner', 'Entity')
    description = fields.Text('Description')
    sampling_point_ids = fields.One2many('lims.sampling.point', 'network_id', 'Sampling Point', readonly=True)
    total_analysis = fields.Integer('Total Analysis', compute='count_analysis')
    total_result = fields.Integer('Total Results', compute='count_result')
    total_compute_result = fields.Integer('Total Compute Results', compute='count_compute_result')
    total_sel_result = fields.Integer('Total Sel Results', compute='count_sel_result')
    total_text_result = fields.Integer('Total Text Results', compute='count_text_result')
    subnetwork_ids = fields.One2many('lims.subnetwork', 'network_id', string="Sub Networks")

    def count_analysis(self):
        for record in self:
            record.total_analysis = sum(sampling_point_id.total_analysis for sampling_point_id in record.sampling_point_ids)

    def count_compute_result(self):
        for record in self:
            record.total_compute_result = sum(sampling_point_id.total_compute_result for sampling_point_id in record.sampling_point_ids)

    def count_sel_result(self):
        for record in self:
            record.total_sel_result = sum(sampling_point_id.total_sel_result for sampling_point_id in record.sampling_point_ids)

    def count_text_result(self):
        for record in self:
            record.total_text_result = sum(
                sampling_point_id.total_text_result for sampling_point_id in record.sampling_point_ids)

    def count_result(self):
        for record in self:
            record.total_result = sum(sampling_point_id.total_result for sampling_point_id in record.sampling_point_ids)

    def get_all_analysis_view(self):
        domain = [('sampling_point_id', 'in', self.sampling_point_ids.ids)]
        return {
            'name': 'Quality Zone Analysis',
            'domain': domain,
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    def get_all_analysis(self):
        return self.env['lims.analysis'].search([('sampling_point_id', 'in', self.sampling_point_ids.ids)])

    def get_all_analysis_result_view(self):
        domain = [('analysis_id', 'in', self.get_all_analysis().ids)]
        return {
            'name': 'Quality Zone Analysis Result',
            'domain': domain,
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def get_all_analysis_sel_result_view(self):
        domain = [('analysis_id', 'in', self.get_all_analysis().ids)]
        return {
            'name': 'Quality Zone Analysis Sel Result',
            'domain': domain,
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_text_result_view(self):
        domain = [('analysis_id', 'in', self.get_all_analysis().ids)]
        return {
            'name': 'Quality Zone Analysis Text Result',
            'domain': domain,
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_compute_result_view(self):
        domain = [('analysis_id', 'in', self.get_all_analysis().ids)]
        return {
            'name': 'Quality Zone Compute Analysis Result',
            'domain': domain,
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,graph,pivot,calendar',
        }
