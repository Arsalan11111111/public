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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    nb_pack = fields.Integer('Packs', compute='compute_info')
    nb_parameter = fields.Integer('Parameters', compute='compute_info')
    nb_method_param_charac = fields.Integer('Charac. Param.', compute='compute_info')

    def compute_info(self):
        for record in self:
            record.nb_pack = self.env['lims.parameter.pack'].search_count([('product_id', '=', record.id)])
            record.nb_parameter = self.env['lims.parameter'].search_count([('product_id', '=', record.id)])
            record.nb_method_param_charac = self.env['lims.method.parameter.characteristic'].search_count([
                ('product_id', '=', record.id)
            ])

    def get_all_pack(self):
        return {
            'name': _('Parameter Pack'),
            'domain': [('product_id', '=', self.id)],
            'res_model': 'lims.parameter.pack',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'default_product_id': self.id},
        }

    def get_all_parameter(self):
        return {
            'name': _('Parameter'),
            'domain': [('product_id', '=', self.id)],
            'res_model': 'lims.parameter',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'default_product_id': self.id},
        }

    def get_all_method_param(self):
        return {
            'name': _('Method Parameter Characteristic'),
            'domain': [('product_id', '=', self.id)],
            'res_model': 'lims.method.parameter.characteristic',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {'default_product_id': self.id},
        }
