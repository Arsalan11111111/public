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


class CreateParameterPackWizard(models.TransientModel):
    _name = 'create.parameter.pack.wizard'
    _description = 'Create Parameter Pack'

    @api.model
    def create_line_ids(self):
        line_ids = self.env['create.parameter.pack.line']
        method_parameter_characteristic_ids = self.env['lims.method.parameter.characteristic'].browse(
                                                    self.env.context.get('default_method_parameter_characteristic_ids'))
        for method_parameter_characteristic in method_parameter_characteristic_ids:
            line_ids += line_ids.new({
                'method_parameter_characteristic_id': method_parameter_characteristic.id,
                'regulation_id': method_parameter_characteristic.regulation_id.id,
                'laboratory_id': method_parameter_characteristic.laboratory_id.id,
                'matrix_id': method_parameter_characteristic.matrix_id.id,
                'rel_state': method_parameter_characteristic.state,
                'rel_active': method_parameter_characteristic.active,
            })
        return line_ids

    line_ids = fields.One2many('create.parameter.pack.line', 'wizard_id', default=create_line_ids)
    name = fields.Char('Name')

    def do_confirm(self):
        self.ensure_one()
        if self.line_ids and len(self.line_ids.mapped('regulation_id')) == 1 and len(self.line_ids.mapped('laboratory_id')) == 1 \
                and len(self.line_ids.mapped('matrix_id')) == 1:
            vals = {
                'regulation_id': self.line_ids[0].regulation_id.id,
                'labo_id': self.line_ids[0].laboratory_id.id,
                'matrix_id': self.line_ids[0].matrix_id.id,
                'name': self.name
            }
            parameter_pack = self.env['lims.parameter.pack'].create(vals)
            for line in self.line_ids:
                vals = {
                    'method_param_charac_id': line.method_parameter_characteristic_id.id,
                    'pack_id': parameter_pack.id
                }
                pack_line = self.env['lims.parameter.pack.line'].create(vals)
            form = self.env.ref('lims_base.lims_parameter_pack_form')
            return {'name': 'Parameter Pack',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': form.id,
                    'res_model': 'lims.parameter.pack',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': parameter_pack.id,
                    }
        raise exceptions.ValidationError(_('Regulation, laboratory and matrix should be the same for all lines'))


class CreateParameterPackLine(models.TransientModel):
    _name = 'create.parameter.pack.line'
    _description = 'Create Parameter Pack Line'

    wizard_id = fields.Many2one('create.parameter.pack.wizard')
    method_parameter_characteristic_id = fields.Many2one('lims.method.parameter.characteristic')
    regulation_id = fields.Many2one('lims.regulation', 'Regulation', related='method_parameter_characteristic_id.regulation_id')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', related='method_parameter_characteristic_id.laboratory_id')
    matrix_id = fields.Many2one('lims.matrix', 'Matrix', related='method_parameter_characteristic_id.matrix_id')
    rel_state = fields.Selection(related='method_parameter_characteristic_id.state')
    rel_active = fields.Boolean(related='method_parameter_characteristic_id.active')
