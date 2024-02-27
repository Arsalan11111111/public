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
from odoo import models, fields, api


class AttributeSelResultWizard(models.TransientModel):
    _name = 'attribute.sel.result.wizard'
    _description = 'Attribute Sel Result'

    sel_result_id = fields.Many2one('lims.analysis.sel.result')
    value_id = fields.Many2one('lims.result.value')
    line_ids = fields.One2many('attribute.sel.result.wizard.line', 'wizard_id')

    rel_analysis_id = fields.Many2one(related='sel_result_id.analysis_id')
    rel_sop_id = fields.Many2one(related='sel_result_id.sop_id')
    rel_parameter_id = fields.Many2one(related='sel_result_id.method_param_charac_id.parameter_id')

    @api.onchange('sel_result_id')
    def _get_default_value_id(self):
        for record in self:
            value_id = record.sel_result_id.mapped('value_id')._origin
            if value_id:
                record.value_id = value_id
                self._get_default_attribute_ids()

    def _get_default_attribute_ids(self):
        line_ids = self.env['attribute.sel.result.wizard.line']
        for record in self:
            attribute_ids = record.env['lims.parameter.attribute'].search([('value_id', '=', record.value_id.id)])
            current_values = record.sel_result_id.mapped('attribute_values_ids').ids
            for attribute in attribute_ids:
                attribute_value_id = False
                attribute_value_ids = attribute.value_ids.ids
                for current in current_values:
                    if current in attribute_value_ids:
                        attribute_value_id = current
                line_ids += line_ids.new({
                    'sel_result_id': record.sel_result_id._origin,
                    'attribute_id': attribute,
                    'attribute_type_id': attribute.attribute_type_id.id,
                    'attribute_value_id': attribute_value_id,
                    'attribute_type_values_ids': attribute_value_ids,
                })
            self.line_ids = line_ids

    def create_attributes_on_result(self):
        for record in self:
            result = record.sel_result_id
            if result.attribute_values_ids != record.line_ids.mapped('attribute_value_id'):
                result.attribute_values_ids = record.line_ids.mapped('attribute_value_id')


class AttributeSelResultWizardLine(models.TransientModel):
    _name = 'attribute.sel.result.wizard.line'
    _description = 'Attribute Sel Result Line'

    wizard_id = fields.Many2one('attribute.sel.result.wizard')
    sel_result_id = fields.Many2one('lims.analysis.sel.result')
    attribute_type_id = fields.Many2one('lims.parameter.attribute.type')
    attribute_id = fields.Many2one('lims.parameter.attribute')
    attribute_value_id = fields.Many2one('lims.parameter.attribute.type.value')
    attribute_type_values_ids = fields.Selection([])


