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

    def compute_lock_button(self):
        for record in self:
            analysis_from_move = record.move_line_ids.mapped('analysis_ids')
            if not analysis_from_move.filtered(lambda a: a.rel_type != 'cancel'):
                record.lock_button = False
            else:
                record.lock_button = True

    def create_analysis(self, laboratory=False, stock_moves=False):
        if self.picking_id and self.picking_id.state not in ['assigned', 'done']:
            raise exceptions.ValidationError(_("Picking should be at least 'Ready'."))

        if self.picking_id and self.picking_id.rel_create_analysis:
            analysis_ids = self.env['lims.analysis']
            add_parameters_obj = self.env['add.parameters.wizard']
            laboratory_obj = self.env['lims.laboratory']

            if not laboratory:
                laboratory = laboratory_obj.search([
                    ('company_id', '=', self.picking_id.company_id.id)
                ], limit=1) or self.picking_id.picking_type_id.laboratory_company_id

            if laboratory:
                if len(laboratory) > 1:
                    raise exceptions.ValidationError(_('This company has multiple laboratories'))
                else:
                    if stock_moves:
                        move_lines_ids = stock_moves.move_line_id
                    else:
                        move_lines_ids = self.move_line_nosuggest_ids
                    for line in move_lines_ids.filtered(
                            lambda m: not m.analysis_ids.filtered(lambda a: a.rel_type != 'cancel')
                    ):
                        vals = self.get_vals_analysis(line)
                        vals['laboratory_id'] = laboratory.id
                        context = self.env.context.copy()
                        # default state : 'draft' (trigger an error)
                        if context.get('default_state'):
                            del context['default_state']
                        # default_location: location_src_id(stock.location)
                        # try to fill location_id(lims.sampling.point.location)
                        # Not the same model
                        if context.get('default_location_id'):
                            del context['default_location_id']
                        nbr = 1
                        if stock_moves:
                            stock_move_lot_wizard_lines = stock_moves.filtered(lambda l: l.move_line_id == line)
                            if stock_move_lot_wizard_lines:
                                nbr = stock_move_lot_wizard_lines[0].nbr_sample
                                lot = stock_move_lot_wizard_lines[0].lot_id
                                vals.update({
                                    'lot_id': lot.id
                                })

                        for i in range(nbr):
                            analysis = analysis_ids.with_context(context).create(vals)
                            add_parameters_id = add_parameters_obj.create({
                                'analysis_id': analysis.id
                            })
                            pack_ids = line.product_id.additional_pack_ids or line.product_id.pack_ids
                            for pack_id in pack_ids:
                                add_parameters_id.parameter_pack_id = pack_id
                                add_parameters_id.create_line_from_pack(pack_id)
                            add_parameters_id.with_context(context).create_results()
                            line.analysis_ids += analysis
                            analysis_ids += analysis
                    if analysis_ids:
                        return {
                            'name': _('Analysis'),
                            'type': 'ir.actions.act_window',
                            'res_model': 'lims.analysis',
                            'view_type': 'form',
                            'view_mode': 'tree,form,pivot,graph,calendar',
                            'target': 'current',
                            'domain': [('id', 'in', analysis_ids.ids)],
                        }
            else:
                raise exceptions.ValidationError(_('No laboratory found for this company'))
        else:
            raise exceptions.ValidationError(_('Picking type don\'t allow to create analysis'))

    def get_vals_analysis(self, line):
        category_id = False
        if self.picking_id:
            category_id = self.picking_id.picking_type_id.analysis_category_id.id
        if 'raw_material_production_id' in self._fields and self.raw_material_production_id:
            category_id = self.raw_material_production_id.picking_type_id.analysis_category_id.id
        return {
            'product_id': line.product_id.id,
            'matrix_id': line.product_id.matrix_id.id,
            'customer_ref': line.reference,
            'date_plan': line.date,
            'category_id': category_id,
            'date_sample_begin': fields.Datetime.now()
        }

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
            return self.create_analysis()
