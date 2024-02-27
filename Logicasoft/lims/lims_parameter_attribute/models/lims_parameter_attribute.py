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


class LimsParameterAttribute(models.Model):
    _name = 'lims.parameter.attribute'
    _description = 'Parameter Attribute'
    _order = 'sequence, id'

    name = fields.Char('Name', compute='_get_default_name',
                       help='Automatic concatenation of  Attribute Type (if exist) and Value')
    sequence = fields.Integer()
    active = fields.Boolean('Active', default=True)

    value_id = fields.Many2one('lims.result.value', required=True, string='Value')
    attribute_type_id = fields.Many2one('lims.parameter.attribute.type')
    value_ids = fields.Many2many('lims.parameter.attribute.type.value', relation='lims_parameter_attribute_values',
                                 string='Values')

    @api.depends('value_id')
    def _get_default_name(self):
        for record in self:
            name = record.value_id.name
            if record.attribute_type_id.name:
                name = record.value_id.name + ' - ' + record.attribute_type_id.name
            record.name = name
