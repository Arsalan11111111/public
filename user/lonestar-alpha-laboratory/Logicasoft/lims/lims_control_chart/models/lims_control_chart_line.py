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
from odoo import fields, models


def type_line_selection():
    return [('measure', 'Measure'), ('target', 'Target'), ('limit1-', 'Limit-1'), ('limit2-', 'Limit-2'),
             ('limit1+', 'Limit+1'), ('limit2+', 'Limit+2')]


class ControlChartLines(models.Model):
    _name = 'lims.control.chart.line'
    _order = 'sequence, id'
    _description = 'Control chart lines'

    sequence = fields.Integer()
    type_line = fields.Selection(type_line_selection(),
                                 help='Defines the type of line this would represent in the graph')
    value = fields.Float('Value', required=True,
                         help='This value will draw a line in the control graph.')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True)
    result_num_id = fields.Many2one('lims.analysis.numeric.result')
    result_com_id = fields.Many2one('lims.analysis.compute.result')
