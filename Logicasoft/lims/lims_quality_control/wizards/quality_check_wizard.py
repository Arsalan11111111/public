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


class QualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(QualityCheckWizard, self).default_get(fields_list)
        context = self.env.context
        stock_picking_id = False
        if ('params' in context) and ('id' in context['params']):
            stock_picking_id = context['params']['id']
        if stock_picking_id:
            res.update({'stock_picking_id': stock_picking_id})
        return res

    rel_create_analysis = fields.Boolean(related='current_check_id.point_id.create_analysis')
    stock_picking_id = fields.Many2one('stock.picking', string="Stock picking")
    rel_code = fields.Selection(related='stock_picking_id.picking_type_id.code')

    def create_analysis(self):
        return self.current_check_id.create_analysis()

    def create_analysis_from_stock_move(self):
        return self.current_check_id.create_analysis_from_stock_move()
