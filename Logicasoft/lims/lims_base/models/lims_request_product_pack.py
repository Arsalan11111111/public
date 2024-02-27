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


def unique_charac(_list):
    return {(line.get('sample_id'), line.get('method_param_charac_id')): line for line in _list}.values()


class LimsRequestProductPack(models.Model):
    _name = 'lims.request.product.pack'
    _order = 'sequence, id'
    _description = 'Request Product Pack'

    name = fields.Char(translate=True)
    request_id = fields.Many2one('lims.analysis.request', 'Request')
    product_id = fields.Many2one('product.product', 'Product')
    pack_ids = fields.Many2many('lims.parameter.pack', string='Parameter Packs', context={'active_test': False})
    qty = fields.Integer('Quantity', default=1)
    sequence = fields.Integer(default=10)
    request_sample_ids = fields.One2many('lims.analysis.request.sample', 'product_pack_id')
    matrix_type_id = fields.Many2one('lims.matrix.type', 'Matrix Type')
    matrix_id = fields.Many2one('lims.matrix', 'Matrix')
    color = fields.Char('Color', default='#FFFFFF')
    location = fields.Char()
    comment = fields.Char('Comment')
    method_param_charac_ids = fields.Many2many('lims.method.parameter.characteristic',
                                               'rel_request_product_pack_method_param', 'product_pack_id',
                                               'method_param_charac_id', string='Parameters',
                                               context={'active_test': False})
    analysis_ids = fields.One2many('lims.analysis', compute="compute_analysis")

    def compute_analysis(self):
        for rec in self:
            rec.analysis_ids = rec.request_sample_ids.analysis_id

    @api.model_create_multi
    def create(self, vals_list):
        """
        Add product form product_id define in request.
        :param vals_list:
        :return:
        """
        for vals in vals_list:
            if vals.get('request_id'):
                if product := self.env['lims.analysis.request'].browse(vals.get('request_id')).product_id:
                    vals.update({
                        'product_id': product.id,
                    })
        return super().create(vals_list)

    @api.onchange('method_param_charac_ids')
    def onchange_parameter_characteristic_ids(self):
        if self.method_param_charac_ids and self.pack_ids and \
                self.method_param_charac_ids.filtered(
                    lambda m: m in self.pack_ids.mapped('parameter_ids.method_param_charac_id')):
            raise exceptions.ValidationError(_('You can\'t add the same parameter twice'))

    @api.onchange('name')
    def onchange_name(self):
        """
        Set the product as the same one than the request
        :return:
        """
        if self.request_id and self.request_id.product_id:
            self.product_id = self.request_id.product_id

    def write(self, vals):
        if vals.get('qty'):
            old_qty = self.qty

        res = super(LimsRequestProductPack, self).write(vals)
        if vals.get('qty'):
            if vals.get('qty') > old_qty:
                self.request_id.generate_request_sample_line()
            elif vals.get('qty') < old_qty:
                all_pack = self.env['lims.parameter.pack']
                all_pack += self.pack_ids.filtered(lambda p: not p.is_pack_of_pack)
                all_pack += self.pack_ids.filtered(lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id')
                qty = self.request_id.sample_ids.filtered(lambda s: s.pack_ids == all_pack and
                                                                    s.method_param_charac_ids == self.method_param_charac_ids)
                if len(qty) > vals.get('qty'):
                    raise exceptions.UserError(_('You must delete samples before changing quantity'))
        return res

    def get_request_sample_value(self, pack_id):
        """
        Get the value for create analysis request sample
        :param pack_id:
        :return:
        """
        return {
            'name': self.name,
            'regulation_id': pack_id.regulation_id.id,
            'request_id': self.request_id.id,
            'matrix_id': self.matrix_id.id,
            'product_pack_id': self.id,
            'auto': True,
            'pack_ids': [(4, pack_id.id)],
            'date_plan': self.request_id.date_plan,
            'comment': self.comment,
            'method_param_charac_ids': [(4, method_param_charac_ids.id) for method_param_charac_ids in self.method_param_charac_ids],
        }

    def add_parameters(self):
        """
        Open the wizard for add parameter
        :return:
        """
        self.ensure_one()
        return {
            'name': _('Add parameters'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.parameters.request.product',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_product_pack_id': self.id}
        }


    @api.onchange('matrix_type_id')
    def onchange_filter_matrix(self):
        if self.matrix_type_id:
            matrix_ids = [('type_id', '=', self.matrix_type_id.id)]
        else:
            matrix_ids = []

        return {'domain': {'matrix_id': matrix_ids}
                }

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and self.product_id.lims_for_analysis:
            self.matrix_id = self.product_id.matrix_id
            pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids
            return {'domain': {'pack_id': [('id', 'in', pack_ids.ids)],
                               }
                    }

    @api.onchange('matrix_id')
    def onchange_matrix_id(self):
        if self.matrix_id:
            return {'domain': {'product_id': [('matrix_id', '=', self.matrix_id.id)],
                               }
                    }

    def open_view_element(self):
        """
        Open element in form (like wizard view) in other elements.
        :return:
        """
        return {
            'name': _('View Form'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def get_regulation(self):
        return False
