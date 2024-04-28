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
from odoo import models, fields, _, api


class MassDuplicateProductLimitWizard(models.TransientModel):
    _name = 'mass.duplicate.product.limit.wizard'
    _description = 'Wizard for mass duplication of product limits'

    def get_domain_product_id(self):
        parameter_char_product_ids = self.env.context.get('default_parameter_char_product_ids')
        char_product_obj = self.env['lims.parameter.char.product']
        parameter_char_product_id = char_product_obj.browse(parameter_char_product_ids)

        matrix_id = parameter_char_product_id.mapped('product_id').mapped('matrix_id')
        return [('lims_for_analysis', '=', True), ('matrix_id', '=', matrix_id.id)]

    duplicate_product_limit_line_ids = fields.One2many('mass.duplicate.product.limit.wizard.line', 'wizard_id')
    product_id = fields.Many2one('product.product', 'Product', domain=get_domain_product_id)
    matrix_id = fields.Many2one('lims.matrix')

    @api.model
    def default_get(self, fields):
        res = super(MassDuplicateProductLimitWizard, self).default_get(fields)
        char_product_obj = self.env['lims.parameter.char.product']
        line_ids = []
        for parameter_char_product_id in self.env.context.get('default_parameter_char_product_ids'):
            parameter_char_product_id = char_product_obj.browse(parameter_char_product_id)
            line_ids.append((0, 0,
                             {
                                 'parameter_char_product_id': parameter_char_product_id.id,
                                 'product_id': parameter_char_product_id.product_id.id,
                                 'method_param_charac_id': parameter_char_product_id.method_param_charac_id.id,
                                 'matrix_id': parameter_char_product_id.product_id.matrix_id.id
                             }))
        res.update({'duplicate_product_limit_line_ids': line_ids})
        return res

    def do_confirm(self):
        new_param_ids = []
        for line_id in self.duplicate_product_limit_line_ids:
            parameter_char_product_id = line_id.parameter_char_product_id
            new_parameter_char_product = parameter_char_product_id.copy({
                'product_id': self.product_id.id
            })
            for limit_id in parameter_char_product_id.limit_ids:
                limit_id.copy({
                    'state': limit_id.state,
                    'parameter_char_product_id': new_parameter_char_product.id
                })
            new_param_ids.append(new_parameter_char_product.id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Parameter char product'),
            'view_mode': 'tree,form',
            'res_model': 'lims.parameter.char.product',
            'domain': [('id', 'in', new_param_ids)]
        }


class MassDuplicateProductLimitWizardLine(models.TransientModel):
    _name = 'mass.duplicate.product.limit.wizard.line'
    _description = 'Line of wizard for mass duplication of product limits'

    wizard_id = fields.Many2one('mass.duplicate.product.limit.wizard', ondelete='cascade')
    parameter_char_product_id = fields.Many2one('lims.parameter.char.product', 'Parameter char product')
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', readonly=True)
    matrix_id = fields.Many2one('lims.matrix', readonly=True)
