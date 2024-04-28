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
from odoo import models, fields, api, _


class ParameterCharacteristicDuplicateWizard(models.TransientModel):
    _name = 'parameter.characteristic.duplicate.wizard'
    _description = 'Wizard duplicate parameter characteristic'

    parameter_characteristic_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter Characteristic')
    regulation_id = fields.Many2one('lims.regulation', 'Regulation')
    matrix_id = fields.Many2one('lims.matrix', 'Matrix')
    method_id = fields.Many2one('lims.method', 'Method')
    parameter_id = fields.Many2one('lims.parameter', 'Parameter')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory')

    @api.onchange('parameter_characteristic_id')
    def onchange_parameter_characteristic_id(self):
        if self.parameter_characteristic_id:
            self.update({
                'regulation_id': self.parameter_characteristic_id.regulation_id.id,
                'matrix_id': self.parameter_characteristic_id.matrix_id.id,
                'method_id': self.parameter_characteristic_id.method_id.id,
                'parameter_id': self.parameter_characteristic_id.parameter_id.id,
                'laboratory_id': self.parameter_characteristic_id.laboratory_id.id,
            })

    def do_duplicate(self):
        defaults = {
            'regulation_id': self.regulation_id.id,
            'matrix_id': self.matrix_id.id,
            'method_id': self.method_id.id,
            'parameter_id': self.parameter_id.id,
            'laboratory_id': self.laboratory_id.id,
        }
        new_param = self.parameter_characteristic_id.copy(default=defaults)
        for limit in self.parameter_characteristic_id.limit_ids:
            limit.copy(default={'method_param_charac_id': new_param.id})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Parameter characteristic'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_param.id,
            'res_model': 'lims.method.parameter.characteristic'
        }
