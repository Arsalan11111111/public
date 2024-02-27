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
from odoo import models, fields, exceptions, _, api


class LimsMethodParameterCharacteristic(models.Model):
    _inherit = 'lims.method.parameter.characteristic'

    billable = fields.Boolean(tracking=True)
    sale_price = fields.Float(related='product_id.list_price', readonly=1, tracking=True)
    rel_parameter_product = fields.Many2one('product.product', 'Parameter\'s product',
                                            related='parameter_id.product_id', store=True)

    def get_product(self, **kwargs):
        self.ensure_one()
        return self.product_id or self.parameter_id.product_id

    def get_field_to_test(self):
        """
        Bypass Validation control, if parameter is in state 'validated'
        :return:
        """
        res = super(LimsMethodParameterCharacteristic, self).get_field_to_test()
        res += [u'billable']
        return res

    @api.constrains('billable', 'product_id', 'rel_parameter_product')
    def check_product_if_billable(self):
        """
        If parameter characteristic is billable, check if there's one product configured either on parameter
        characteristic or on parent parameter
        """
        for record in self.filtered(lambda m: m.billable and not m.product_id):
            if not record.rel_parameter_product:
                raise exceptions.ValidationError(
                    _("A product must be configured on parameter characteristic {} or its parameter in order for it to"
                      " be billable").format(record.name))
