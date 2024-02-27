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


class AddParametersRequest(models.TransientModel):
    _name = 'add.parameters.request.product'
    _description = 'Add Parameter Request'

    def get_request_line(self):
        request_line_obj = self.env['add.parameters.request.product.line']
        request_line_ids = request_line_obj
        request_product_id = self.env['lims.request.product.pack'].browse(self.env.context.get('default_request_product_pack_id'))

        all_pack = request_product_id.pack_ids.filtered(lambda p: p.active and p.state == 'validated')
        unique_method_param_charac_ids = self.env['lims.method.parameter.characteristic']

        for pack_id in set(all_pack):
            vals = {
                'pack_id': pack_id.id,
                'in_request': True,
            }
            if pack_id.parameter_ids:
                for method_param_charac_id in pack_id.parameter_ids.mapped('method_param_charac_id').\
                        filtered(lambda m: m.active and m.state == 'validated'):
                    vals.update({
                        'method_param_charac_id': method_param_charac_id.id
                    })
                    request_line_ids += request_line_obj.new(vals)
                    unique_method_param_charac_ids += method_param_charac_id
            else:
                request_line_ids += request_line_obj.new(vals)

        for method_param_charac_id in request_product_id.method_param_charac_ids.filtered(
                lambda p: p not in unique_method_param_charac_ids and p.active and p.state == 'validated'
        ):
            vals = {
                'method_param_charac_id': method_param_charac_id.id,
                'in_request': True,
            }
            request_line_ids += request_line_obj.new(vals)
            unique_method_param_charac_ids += method_param_charac_id

        return request_line_ids

    add_parameters_request_line_ids = fields.One2many('add.parameters.request.product.line', 'add_parameters_request_id',
                                                      default=get_request_line)
    request_product_pack_id = fields.Many2one('lims.request.product.pack')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter')
    pack_id = fields.Many2one('lims.parameter.pack', 'Pack')
    rel_request_id = fields.Many2one('lims.analysis.request', related='request_product_pack_id.request_id')
    rel_matrix_id = fields.Many2one('lims.matrix', related='request_product_pack_id.matrix_id')
    rel_laboratory_id = fields.Many2one('lims.laboratory', related='rel_request_id.labo_id')

    @api.onchange('pack_id')
    def onchange_pack_id(self):
        """
        When a parameter pack is added create results for its parameters.
        :return: (None)
        """
        self.create_line_from_pack(self.pack_id)

    def create_line_from_pack(self, pack_id):
        all_pack = self.env['lims.parameter.pack']
        all_pack += pack_id.filtered(lambda p: not p.is_pack_of_pack)
        all_pack += pack_id.filtered(lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id').filtered(
            lambda p: p.active and p.state == 'validated'
        )

        request_line_obj = self.env['add.parameters.request.product.line']
        for pack_id in set(all_pack):
            if pack_id not in self.add_parameters_request_line_ids.mapped('pack_id'):
                vals = {
                    'pack_id': pack_id.id,
                }
                if pack_id.parameter_ids:
                    for method_param_charac_id in pack_id.parameter_ids.mapped('method_param_charac_id').\
                            filtered(lambda m: m.active and m.state == 'validated'):
                        if method_param_charac_id not in self.add_parameters_request_line_ids.\
                                mapped('method_param_charac_id'):
                            vals.update({
                                'method_param_charac_id': method_param_charac_id.id
                            })
                            self.add_parameters_request_line_ids += request_line_obj.new(vals)

                            for sub_method_param_charac_id in method_param_charac_id.conditional_parameters_ids.\
                                    filtered(lambda p: p.active and p.state == 'validated'):
                                if sub_method_param_charac_id not in self.add_parameters_request_line_ids.\
                                        mapped('method_param_charac_id'):
                                    vals = {
                                        'method_param_charac_id': sub_method_param_charac_id.id,
                                        'is_conditional_parameter': True
                                    }
                                    self.add_parameters_request_line_ids += request_line_obj.new(vals)
                else:
                    self.add_parameters_request_line_ids += request_line_obj.new(vals)

    @api.onchange('method_param_charac_id')
    def onchange_parameter_characteristic_id(self):
        """
        When a parameter is added create result for it.
        :return: (None)
        """
        if self.method_param_charac_id:
            request_line_obj = self.env['add.parameters.request.product.line']

            if self.method_param_charac_id not in self.add_parameters_request_line_ids.mapped('method_param_charac_id'):
                vals = {
                    'method_param_charac_id': self.method_param_charac_id.id,
                }
                self.add_parameters_request_line_ids += request_line_obj.new(vals)

                for sub_method_param_charac_id in self.method_param_charac_id.conditional_parameters_ids.filtered(
                        lambda p: p.active and p.state == 'validated'
                ):
                    if sub_method_param_charac_id not in self.add_parameters_request_line_ids.\
                            mapped('method_param_charac_id'):
                        vals = {
                            'method_param_charac_id': sub_method_param_charac_id.id,
                            'is_conditional_parameter': True
                        }
                        self.add_parameters_request_line_ids += request_line_obj.new(vals)
            else:
                raise exceptions.ValidationError(_('You can\'t add the same parameter twice'))

    def update_line(self):
        for line_id in self.add_parameters_request_line_ids.filtered(lambda l: not l.in_request):
            if line_id.pack_id and (not line_id.method_param_charac_id) and (
                    line_id.pack_id not in self.request_product_pack_id.pack_ids
            ):
                self.request_product_pack_id.write({
                    'pack_ids': [(4, line_id.pack_id.id)]
                })
            elif not line_id.pack_id and line_id.method_param_charac_id and (
                    line_id.method_param_charac_id not in self.request_product_pack_id.method_param_charac_ids
            ):
                self.request_product_pack_id.write({
                    'method_param_charac_ids': [(4, line_id.method_param_charac_id.id)],
                })
            elif line_id.pack_id and line_id.method_param_charac_id:
                vals = {}
                if line_id.method_param_charac_id not in self.request_product_pack_id.method_param_charac_ids:
                    vals.update({
                        'method_param_charac_ids': [(4, line_id.method_param_charac_id.id)]
                    })
                if line_id.pack_id not in self.request_product_pack_id.pack_ids:
                    vals.update({
                        'pack_ids': [(4, line_id.pack_id.id)]
                    })
                if vals:
                    self.request_product_pack_id.write(vals)


class AddParametersRequestLine(models.TransientModel):
    _name = 'add.parameters.request.product.line'
    _description = 'Add Parameter Request Line'

    add_parameters_request_id = fields.Many2one('add.parameters.request.product', ondelete='cascade')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter')
    pack_id = fields.Many2one('lims.parameter.pack', 'Pack')
    in_request = fields.Boolean()
    is_conditional_parameter = fields.Boolean()
