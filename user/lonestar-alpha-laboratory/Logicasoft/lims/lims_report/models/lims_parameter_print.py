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
from odoo import models, fields, api, exceptions, _


class LimsParameterPrint(models.Model):
    _name = 'lims.parameter.print'
    _order = 'sequence, id'
    _description = 'Parameter Print'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    print_name = fields.Char('Print Name', translate=True, required=True, default='/',
                             help="The name that will be printed on reports for the linked parameters.")
    sequence = fields.Integer('Sequence', default=5)
    print_group_ids = fields.Many2many('lims.parameter.print.group',
                                       'parameter_print_group_relation',
                                       'parameter_print_id',
                                       'parameter_group_id',
                                       'Print Groups',
                                       help="The group that will regroup parameter print on the report.")
    parameter_characteristic_ids = fields.One2many('lims.method.parameter.characteristic', 'parameter_print_id',
                                                   'Parameter Characteristics',
                                                   help="The parameters that will be represented by this parameter "
                                                        "print.")

    number_parameter = fields.Integer('Number of Parameters', compute='get_number_of_parameter')
    report_note = fields.Char()
    is_default_print_on_report = fields.Boolean('By default print result', default=True,
                                                help="For each result line generated by this parameter print copy this "
                                                     "'Print Result' value.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('print_name') and vals.get('print_name') == '/':
                vals['print_name'] = vals.get('name')
        return super().create(vals_list)

    def get_number_of_parameter(self):
        """
        Compute the number of parameter linked to this parameter.print
        :return: (None)
        """
        for record in self:
            record.number_parameter = len(record.parameter_characteristic_ids)
