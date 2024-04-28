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
from odoo import fields, models, api, exceptions, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    rel_lims_for_analysis = fields.Boolean(related='product_id.lims_for_analysis',
                                           help="The button 'Lims for analysis' linked with the product.")
    lock_button = fields.Boolean(compute='compute_lock_button',
                                 help="This is checked if the analysis on these move lines are not all cancelled.")

    @api.depends('move_line_ids')
    def compute_lock_button(self):
        for record in self:
            lock_button = False
            if record.move_line_ids.filtered("lock_button"):
                lock_button = True
            record.lock_button = lock_button

    def open_create_analysis_wizard(self):
        self.ensure_one()
        if self.env.user.has_group('stock.group_production_lot'):
            return {
                'name': _('Stock Move Lot'),
                'type': 'ir.actions.act_window',
                'res_model': 'stock.move.lot.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_stock_move_id': self.id,
                }
            }
        else:
            if not self.move_line_ids:
                raise exceptions.ValidationError(_("There is no move's lines."))
            analysis = self.move_line_ids.create_analysis()
            return {
                'name': _('Analysis'),
                'type': 'ir.actions.act_window',
                'res_model': 'lims.analysis',
                'view_type': 'form',
                'view_mode': 'tree,form,pivot,graph,calendar',
                'target': 'current',
                'domain': [('id', 'in', analysis.ids)],
            }
