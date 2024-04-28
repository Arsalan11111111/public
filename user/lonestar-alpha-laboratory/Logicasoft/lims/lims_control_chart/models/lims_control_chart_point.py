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
from ..models.lims_control_chart_line import type_line_selection


class LimsControlChartPoint(models.Model):
    _name = 'lims.control.chart.point'
    _description = 'Control Chart Point'

    value = fields.Float(string="Measure")
    type_line = fields.Selection(type_line_selection())
    result_num_id = fields.Many2one('lims.analysis.numeric.result')
    result_com_id = fields.Many2one('lims.analysis.compute.result')
    method_id = fields.Many2one('lims.method.parameter.characteristic')
    sop_id = fields.Many2one('lims.sop', store=True, compute='_get_point_datas')
    result_stage_id = fields.Many2one('lims.result.stage', store=True, compute='_get_point_datas')
    date_start = fields.Datetime(string="Date Start", compute='_get_point_datas', store=True)
    date_result = fields.Datetime(string="Date Result", compute='_get_point_datas', store=True)
    date_sample = fields.Datetime(string="Date Sample", compute='_get_point_datas', store=True)
    partner_id = fields.Many2one('res.partner', compute='_get_point_datas', store=True)
    user_id = fields.Many2one('res.users', compute='_get_point_datas', string="Operator Input", store=True)
    laboratory_id = fields.Many2one('lims.laboratory', compute='_get_point_datas', store=True)
    department_id = fields.Many2one('lims.department', compute='_get_point_datas', store=True)

    @api.depends('result_num_id', 'result_com_id')
    def _get_point_datas(self):
        for record in self:
            record_id = False
            if record.result_num_id:
                record_id = record.result_num_id
            elif record.result_com_id:
                record_id = record.result_com_id
            self.update({
                'sop_id': record_id.sop_id if record_id else False,
                'result_stage_id': record_id.stage_id if record_id else False,
                'date_start': record_id.date_start if record_id else False,
                'date_result': record_id.date_result if record_id else False,
                'date_sample': record_id.rel_date_sample if record_id else False,
                'partner_id': record_id.rel_partner_id if record_id else False,
                'user_id': record_id.user_id if record_id else False,
                'laboratory_id': record_id.rel_laboratory_id if record_id else False,
                'department_id': record_id.rel_department_id if record_id else False,
            })
