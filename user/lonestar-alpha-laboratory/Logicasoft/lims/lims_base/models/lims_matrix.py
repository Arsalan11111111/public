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
from odoo import fields, models, api, _


class LimsMatrix(models.Model):
    _name = 'lims.matrix'
    _description = 'Matrix'
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
    name = fields.Char('Name', required=True, translate=True, index=True)
    description = fields.Text(string='Description', translate=True)
    type_id = fields.Many2one('lims.matrix.type', string='Matrix Type', index=True)
    nb_parameter_pack = fields.Integer(compute='compute_info')
    nb_method_param_charac = fields.Integer(compute='compute_info')
    product_id = fields.Many2one('product.product', 'Product', index=True)
    active = fields.Boolean('Active', default=True)

    def compute_info(self):
        """
        Compute number of parameter pack where the matrix is in,
        Compute number of method parameter characteristic where the matrix is in
        :return:
        """

        if self.ids:
            pack_counted_data = self.env['lims.parameter.pack'].read_group([('matrix_id', 'in', self.ids)], ['matrix_id'], ['matrix_id'])
            pack_mapped_data = { count['matrix_id'][0]: count['matrix_id_count'] for count in pack_counted_data }
            method_counted_data = self.env['lims.method.parameter.characteristic'].read_group([('matrix_id', 'in', self.ids)], ['matrix_id'], ['matrix_id'])
            method_mapped_data = { count['matrix_id'][0]: count['matrix_id_count'] for count in method_counted_data }
        else:
            pack_mapped_data = {}
            method_mapped_data = {}

        for record in self:
            record.nb_parameter_pack = pack_mapped_data.get(record.id, 0)
            record.nb_method_param_charac = method_mapped_data.get(record.id, 0)

    def action_parameter_pack(self):
        """
        Open the view on parameter pack where matrix is in
        :return:
        """
        return {
            'name': _('Parameter packs'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.parameter.pack',
            'view_mode': 'tree,form',
            'domain': [('matrix_id', '=', self.id)],
            'context': {'default_matrix_id': self.id},
        }

    def action_method_parameter_characteristic(self):
        """
        Open the view on method parameter characteristic where the matrix is in
        :return:
        """
        return {
            'name': _('Method parameter characteristics'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.method.parameter.characteristic',
            'view_mode': 'tree,form',
            'domain': [('matrix_id', '=', self.id)],
            'context': {'default_matrix_id': self.id},
        }
