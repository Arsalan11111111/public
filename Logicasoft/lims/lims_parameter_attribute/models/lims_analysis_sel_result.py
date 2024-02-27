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
from odoo import fields, models, _


class LimsAnalysisSelResult(models.Model):
    _inherit = 'lims.analysis.sel.result'

    attribute_values_ids = fields.Many2many('lims.parameter.attribute.type.value', "rel_result_attributes", 'col1',
                                            'col2', copy=False)
    rel_is_attribute = fields.Boolean(related='method_param_charac_id.parameter_id.is_attribute')

    def open_attributes(self):
        """
        Open the wizard attributes on result
        :return:
        """
        return {
            'name': 'Attributes on results',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attribute.sel.result.wizard',
            'context': {'default_sel_result_id': self.id},
            'target': 'new',
        }

    def write(self, vals):
        res = super(LimsAnalysisSelResult, self).write(vals)
        if 'attribute_values_ids' in vals:
            for record in self:
                attribute_text = ""
                if vals['attribute_values_ids'][0][2]:
                    attributes_values = record.env['lims.parameter.attribute.type.value'].browse(vals['attribute_values_ids'][0][2]).mapped('name')
                    for attribute in attributes_values:
                        attribute_text += " \"{}\" ".format(attribute)
                record.analysis_id.message_post(
                    body=_("Result with parameter: {} and value : {} with attributes : {}").format(
                        record.method_param_charac_id.display_name,
                        record.value_id.name,
                        attribute_text if attribute_text != "" else "\n None"
                    )
                )
        return res
