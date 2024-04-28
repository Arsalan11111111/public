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
from odoo import fields, models


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    service_type_id = fields.Many2one('lims.service.type', 'Service type')

    def create_sale_order(self):
        order_vals = {
            'service_type_id': self.service_type_id and self.service_type_id.id,
        }
        res = super(LimsAnalysisRequest, self.with_context(order_vals=order_vals)).create_sale_order()
        order_id = self.env['sale.order'].browse(res.get('res_id'))
        if order_id.service_type_id and order_id.service_type_id.markup_fees_id:
            product_id = order_id.service_type_id.markup_fees_id

            price_fee = 0
            new_line_vals = {
                'order_id': order_id.id,
                'product_id': product_id.id,
                'product_uom_qty': 1,
                'sequence': 999,
            }
            order_markup = order_id.service_type_id.markup
            partner_services = self.env['lims.partner.service.type'].search(
                [('partner_id', '=', order_id.partner_id.id),
                 ('service_type_id', '=', order_id.service_type_id.id), '|',
                 ('product_id', 'in', order_id.order_line.product_id.ids), ('product_id', '=', False)])
            for order_line in order_id.order_line:
                partner_service = partner_services.filtered(lambda p:
                                                            not p.product_id or p.product_id == order_line.product_id)
                if partner_service:
                    markup = partner_service.markup
                else:
                    markup = order_markup
                price_fee += (order_line.price_unit / 100) * markup * order_line.product_uom_qty
            new_line_vals.update({'price_unit': price_fee})
            self.env['sale.order.line'].create(new_line_vals)
        return res
