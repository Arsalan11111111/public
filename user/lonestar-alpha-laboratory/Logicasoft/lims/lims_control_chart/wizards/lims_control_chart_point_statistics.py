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
import statistics

from odoo import models, fields, api


class ControlChartPointStatistic(models.TransientModel):
    _name = 'lims.control.chart.point.statistics'
    _description = 'Lims Control Chart Point Statistics'

    control_chart_point_ids = fields.Many2many('lims.control.chart.point', 'results')
    average = fields.Float('Average', compute='compute_statistic', digits='Analysis Result')
    median = fields.Float('Median', compute='compute_statistic', digits='Analysis Result',
                          help="Return the median (middle value) of numeric data")

    pvariance = fields.Float('pvariance', compute='compute_statistic', digits='Analysis Result',
                             help="Return the population variance of data")
    variance = fields.Float('variance', compute='compute_statistic', digits='Analysis Result',
                            help="Return the sample variance of data")
    pstdev = fields.Float('pstdev', compute='compute_statistic', digits='Analysis Result',
                          help="Return the square root of the population variance")
    stdev = fields.Float('stdev', compute='compute_statistic', digits='Analysis Result',
                         help="Return the square root of the sample variance")

    minValue = fields.Float('min', compute='compute_statistic', digits='Analysis Result')
    maxValue = fields.Float('max', compute='compute_statistic', digits='Analysis Result')
    nValue = fields.Integer('count', compute='compute_statistic')

    @api.depends('nValue')
    def compute_statistic(self):
        average = 0.0
        median = 0.0
        nValue = 0
        minValue = 0.0
        maxValue = 0.0
        pvariance = 0.0
        variance = 0.0
        pstdev = 0.0
        stdev = 0.0
        values = self.control_chart_point_ids.filtered(lambda l: l.type_line == 'measure').mapped('value')
        if values:
            average = statistics.mean(values)
            median = statistics.median(values)
            nValue = len(values)
            minValue = min(values)
            maxValue = max(values)
            if nValue > 1:
                pvariance = statistics.pvariance(values)
                variance = statistics.variance(values)
                pstdev = statistics.pstdev(values)
                stdev = statistics.stdev(values)
        self.update({
                'average': average,
                'median': median,
                'nValue': nValue,
                'minValue': minValue,
                'maxValue': maxValue,
                'pvariance': pvariance,
                'variance': variance,
                'pstdev': pstdev,
                'stdev': stdev,
            })
