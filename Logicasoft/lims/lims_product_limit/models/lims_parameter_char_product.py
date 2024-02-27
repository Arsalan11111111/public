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


class LimsParameterCharProduct(models.Model):
    _name = 'lims.parameter.char.product'
    _description = 'Parameter Char Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'
    _tracking_parent = 'method_param_charac_id'

    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True,
                                             tracking=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', domain=[('lims_for_analysis', '=', True)], required=True,
                                 tracking=True,
                                 help="Only products for which LIMS (for analysis) is configured are listed. "
                                      "It is not recommended to create product using this menu.")
    reference = fields.Char('Reference', tracking=True)
    comment = fields.Char('Comment', translate=True, tracking=True)
    matrix_id = fields.Many2one('lims.matrix', string='Matrix', tracking=True)
    limit_ids = fields.One2many('lims.method.parameter.characteristic.limit.product', 'parameter_char_product_id')
    report_limit_value = fields.Char('Report Limit Value', translate=True)
    accreditation = fields.Selection([('inta', 'Internal Accredited'), ('intna', ' Internal Not Accredited'),
                                      ('exta', 'External Accredited'), ('extna', 'External Not Accredited')],
                                     string='Accreditation Type', tracking=True)
    accreditation_ids = fields.Many2many('lims.accreditation', string='Organisms', tracking=True)
    rel_matrix_id = fields.Many2one(related='product_id.matrix_id', string="Product's matrix")
    rel_regulation_id = fields.Many2one('lims.regulation', related='method_param_charac_id.regulation_id')

    def open_limit(self):
        """
        Open view on limits for editing it
        :return:
        """
        return {'name': _('Parameter Char Product'),
                'view_mode': 'form',
                'res_model': 'lims.parameter.char.product',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.id,
                }

    def mass_duplicate(self):
        matrix_ids = self.mapped('product_id').mapped('matrix_id')
        if len(matrix_ids) > 1:
            raise exceptions.UserError(_("Should be same matrix for all the product involved"))

        return {
            'name': _('Mass duplicate'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mass.duplicate.product.limit.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_parameter_char_product_ids': self.ids}
        }

