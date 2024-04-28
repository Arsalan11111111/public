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


class StockMoveLotWizard(models.TransientModel):
    _name = 'stock.move.lot.wizard'
    _description = 'Stock Move Lot Wizard'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        stock_move = self.env['stock.move'].browse(self.env.context.get('default_stock_move_id'))
        if stock_move:
            product_id = stock_move.product_id
            laboratory = product_id.pack_ids[0].labo_id if product_id.pack_ids else False
            if not laboratory:
                laboratory = stock_move.picking_id.picking_type_id.laboratory_company_id
            lines = []
            for move_line in stock_move.move_line_ids:
                lines.append(
                    (0, 0, {'move_line_id': move_line.id, 'lot_id': move_line.lot_id.id, 'qty_done': move_line.qty_done})
                )
            res.update({
                'line_ids': lines,
                'laboratory_id':  laboratory.id if laboratory else False
            })
        return res

    stock_move_id = fields.Many2one('stock.move')
    rel_product_id = fields.Many2one(related='stock_move_id.product_id',
                                     help="This is the product of the stock move.")
    rel_quantity_done = fields.Float(related='stock_move_id.quantity_done',
                                     help="This is the quantity done of the stock move.")
    rel_product_uom = fields.Many2one(related='stock_move_id.product_uom',)
    line_ids = fields.One2many('stock.move.lot.wizard.line', 'link_id')
    rel_company_id = fields.Many2one(related='stock_move_id.company_id', store=True,
                                     help="This is the company of the stock move.")
    rel_product_tracking = fields.Selection(related='rel_product_id.tracking')
    rel_product_detailed_type = fields.Selection(related='rel_product_id.detailed_type')
    laboratory_id = fields.Many2one('lims.laboratory')

    def confirm(self):
        self.ensure_one()
        if not self.line_ids.move_line_id:
            raise exceptions.ValidationError(_("There is no move's lines."))
        ids = []
        for line in self.line_ids:
            analysis = line.move_line_id.create_analysis(laboratory=self.laboratory_id, lot=line.lot_id, nbr=line.nbr_sample)
            ids += analysis.ids
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('id', 'in', ids)],
        }


class StockMoveLotWizardLine(models.TransientModel):
    _name = 'stock.move.lot.wizard.line'
    _description = 'Stock Move Lot Wizard Line'

    link_id = fields.Many2one('stock.move.lot.wizard')
    move_line_id = fields.Many2one('stock.move.line')
    lot_id = fields.Many2one('stock.lot', string="Lot/serial number")
    qty_done = fields.Float(string="Done")
    nbr_sample = fields.Integer(string="Nbr Sample", default=1)
