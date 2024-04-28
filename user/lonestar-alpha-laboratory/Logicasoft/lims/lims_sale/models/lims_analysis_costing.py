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


class LimsAnalysisCosting(models.Model):
    _name = 'lims.analysis.costing'
    _order = 'sequence,id'
    _description = 'Lims Analysis Costing'

    sequence = fields.Integer(default=1)
    qty = fields.Integer(default=1)
    analysis_id = fields.Many2one('lims.analysis')
    product_id = fields.Many2one('product.product', 'Product')
    cost = fields.Float('Cost')
    revenue = fields.Float('Revenue')
    pack_ids = fields.Many2many('lims.parameter.pack')
    method_param_charac_ids = fields.Many2many('lims.method.parameter.characteristic')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            final_price = self.product_id.list_price
            if self.analysis_id.pricelist_id:
                final_price, rule_id = self.analysis_id.pricelist_id.\
                    get_product_price_rule(self.product_id, 1.0, self.analysis_id.partner_id)
            self.cost = self.product_id.standard_price * self.qty
            self.revenue = final_price * self.qty
