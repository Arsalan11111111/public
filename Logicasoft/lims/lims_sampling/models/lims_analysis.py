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


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    sampling_point_id = fields.Many2one('lims.sampling.point', 'Sampling Point', tracking=True,
                                        domain="[('matrix_id', '=', matrix_id)]")
    location_id = fields.Many2one('lims.sampling.point.location', 'Location', tracking=True)
    sampling_type_id = fields.Many2one('lims.sampling.type', 'Sampling type')
    quality_zone_id = fields.Many2one('lims.quality.zone', 'Quality zone')
    tank = fields.Char("Tank")

    def get_value_of_result_id(self, result_id):
        result_vals = super(LimsAnalysis, self).get_value_of_result_id(result_id)
        result_vals['sampling_point'] = result_id.analysis_id.sampling_point_id and \
                                        result_id.analysis_id.sampling_point_id.name or ''
        return result_vals

    @api.onchange('matrix_id')
    def onchange_matrix_id_filter_sampling(self):
        if self.matrix_id and self.sampling_point_id and self.sampling_point_id.matrix_id != self.matrix_id:
            raise exceptions.ValidationError(_('The sampling point matrix must be the same as the one in the analysis'))

    @api.onchange('sampling_point_id')
    def onchange_sampling_point_id(self):
        if self.sampling_point_id and (self.sampling_point_id.matrix_id == self.matrix_id or not self.matrix_id):
            self.location_id = self.sampling_point_id.location_id
            self.partner_id = self.sampling_point_id.partner_id
            self.matrix_id = self.sampling_point_id.matrix_id
            self.sampling_type_id = self.sampling_point_id.sampling_type_id
            self.quality_zone_id = self.sampling_point_id.quality_zone_id
        elif self.sampling_point_id and self.matrix_id:
            raise exceptions.ValidationError(_('The sampling point matrix must be the same as the one in the analysis'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sampling_point_id'):
                self.update_vals_for_sampling(vals)
        return super(LimsAnalysis, self).create(vals_list)

    def write(self, vals):
        if vals.get('sampling_point_id'):
            self.update_vals_for_sampling(vals)
        return super(LimsAnalysis, self).write(vals)

    def update_vals_for_sampling(self, vals):
        sampling_point_id = self.env['lims.sampling.point'].browse(vals.get('sampling_point_id'))
        vals.update({
            'location_id': vals.get('location_id') or sampling_point_id.location_id.id,
            'partner_id': vals.get('partner_id') or sampling_point_id.partner_id.id,
            'matrix_id': sampling_point_id.matrix_id.id,
            'sampling_type_id': vals.get('sampling_type_id') or sampling_point_id.sampling_type_id.id,
            'quality_zone_id': vals.get('quality_zone_id') or sampling_point_id.quality_zone_id.id,
        })
        return vals

    def get_vals_for_recurrence(self):
        """
        Set sampling point and location when copy create recurrence on analysis
        :return:
        """
        vals = super(LimsAnalysis, self).get_vals_for_recurrence()
        vals['sampling_point_id'] = self.sampling_point_id and self.sampling_point_id.id or False
        vals['location_id'] = self.location_id and self.location_id.id or False
        vals['sampling_type_id'] = self.sampling_type_id and self.sampling_type_id.id or False
        vals['quality_zone_id'] = self.quality_zone_id and self.quality_zone_id.id or False
        return vals
