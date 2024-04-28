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
from odoo import models, fields, _, api, Command


class GenerateLimitProductVariantWizard(models.TransientModel):
    _name = 'generate.limit.product.variant.wizard'
    _description = 'Wizard for generate limit in all linked variant'

    is_option_overwrite = fields.Boolean('Overwrite',
                                         help="This will remove the existing limits and replace "
                                              "them with the limits defined by the selected product variant.")
    product_template_id = fields.Many2one('product.template', domain="[('lims_for_analysis','=',True)]")
    product_product_id = fields.Many2one('product.product')
    rel_product_active = fields.Boolean(related='product_product_id.active')
    product_product_ids = fields.Many2many('product.product', string='Affected products')
    product_char_limit_ids = fields.Many2many('lims.parameter.char.product',
                                              relation='limit_product_variant_wizard_lims_parameter_char_product_rel')

    def delete_exsiting_limits(self):
        limits = self.env['lims.parameter.char.product'].search([('product_id', 'in', self.product_product_ids.ids)])
        if limits:
            limits.unlink()

    def do_confirm(self):
        """
        Generate duplicate of product_char_limit_ids limits for selected product_product_ids.
        If is_option_overwrite == True, remove existing limits in selected product_product_ids before generation.

        :return:
        """
        if self.is_option_overwrite:
            self.delete_exsiting_limits()
        for product in self.product_product_ids:
            for limit in self.product_char_limit_ids:
                dictonnary_limit_line_list = [limit_line.copy_data()[0] for limit_line in limit.limit_ids]
                # Use copy in place of copy_data because manage the translations.
                limit.copy(
                    {'product_id': product.id, 'limit_ids': [Command.create(x) for x in dictonnary_limit_line_list]}
                )
        return {
            'name': _('Product limits'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'lims.parameter.char.product',
            'domain': [('product_id', 'in', self.product_product_ids.ids if self.product_product_ids else [])]
        }

    @api.onchange('product_product_id')
    def get_product_product_ids(self):
        if self.product_product_id:
            if not self.product_template_id:
                self.product_template_id = self.product_product_id.product_tmpl_id
            self.product_product_ids = self.product_template_id.product_variant_ids.filtered(
                lambda p: p.id != self.product_product_id.id)
            if self.product_product_ids:
                self.product_char_limit_ids = self.env['lims.parameter.char.product'].search(
                    [('product_id', '=', self.product_product_id.id)])
        else:
            self.product_product_ids = False
            self.product_char_limit_ids = False

    @api.onchange('product_template_id')
    def set_default_product_id(self):
        for record in self:
            if not record.product_product_id:
                record.product_product_id = record.product_template_id.product_variant_id
