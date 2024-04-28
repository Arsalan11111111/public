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


class LimsAnalysisComputeResult(models.Model):
    _inherit = 'lims.analysis.compute.result'

    control_chart_line_ids = fields.One2many('lims.control.chart.line', 'result_com_id')
    control_chart_points_ids = fields.One2many('lims.control.chart.point', 'result_com_id')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            if record.method_param_charac_id.is_control_chart:
                record.control_chart_line_ids = record.env['lims.control.chart.line'].search(
                    [('method_param_charac_id', '=', record.method_param_charac_id.id),
                     ('type_line', 'not ilike', 'measure')])
                for line in record.control_chart_line_ids:
                    record.control_chart_points_ids.create([{'value': line.value, 'type_line': line.type_line,
                                                           'result_com_id': line.result_com_id.id,
                                                           'method_id': line.method_param_charac_id.id}])
        return res

    def write(self, vals):
        if 'value' in vals:
            self.update_measure_value(vals.get('value'))
        return super(LimsAnalysisComputeResult, self).write(vals)

    def update_measure_value(self, value=False):
        for record in self:
            if record.method_param_charac_id.is_control_chart:
                records = record.env['lims.control.chart.point'].search(
                    [('result_com_id.id', '=', record.id), ('type_line', 'ilike', 'measure')]
                )
                if len(records) != 1:
                    for item in records:
                        item.sudo().unlink()
                    record.control_chart_points_ids.sudo().create(
                        [{'value': value,
                          'type_line': 'measure',
                          'result_com_id': record.id,
                          'method_id': record.method_param_charac_id.id,
                        }])
                else:
                    records[0].sudo().update({'value': value})

