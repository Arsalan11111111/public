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


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    analysis_ids = fields.Many2many('lims.analysis', string="Analysis created")
    nb_analysis = fields.Integer("Numbers of analysis created", compute='compute_nb_analysis')
    rel_point_id_create_analysis = fields.Boolean(related='point_id.create_analysis')
    rel_picking_code = fields.Selection(related='picking_id.picking_type_id.code')
    rel_production_code = fields.Selection(related='production_id.picking_type_id.code')
    rel_lims_for_analysis = fields.Boolean(related='product_id.lims_for_analysis')

    def get_laboratory(self):
        self.ensure_one()
        pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids
        laboratory = pack_ids[0].labo_id if pack_ids else False
        if not laboratory:
            laboratory = self.env['lims.laboratory'].sudo().search([('default_laboratory', '=', True)], limit=1)
        return laboratory

    def get_category(self):
        self.ensure_one()
        category = self.point_id.analysis_category_id
        if not category:
            laboratory = self.get_laboratory()
            category = laboratory.default_analysis_category_id
        return category

    @api.depends('analysis_ids')
    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.analysis_ids)

    def create_analysis(self, lot=False):
        self.ensure_one()
        if not self.product_id:
            raise exceptions.ValidationError(_("No product inserted"))
        elif not self.product_id.lims_for_analysis:
            raise exceptions.ValidationError(_("Product have boolean 'Lims For Analysis' uncheck"))
        elif not self.product_id.matrix_id:
            raise exceptions.ValidationError(_("Product have no matrix"))
        elif not self.point_id.create_analysis:
            raise exceptions.ValidationError(_("The 'Create analysis' boolean is unchecked on control point."))

        analysis_obj = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']

        laboratory = self.get_laboratory()
        category = self.get_category()
        pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids

        new_analysis = analysis_obj.create({
            'product_id': self.product_id.id,
            'lot_id': lot.id if lot else self.lot_id.id,
            'date_plan': fields.Datetime.now(),
            'date_sample': fields.Datetime.now(),
            'matrix_id': self.product_id.matrix_id.id,
            'customer_ref': self.name,
            'pack_ids': [(6, 0, pack_ids.ids)],
            'laboratory_id': laboratory.id,
            'category_id': category.id
        })
        self.analysis_ids = [(4, new_analysis.id)]
        # copy from stock_move.py in lims_stock
        add_parameters_id = add_parameters_obj.create({
            'analysis_id': new_analysis.id
        })
        for pack_id in new_analysis.pack_ids:
            add_parameters_id.parameter_pack_id = pack_id
            add_parameters_id.create_line_from_pack(pack_id)
        add_parameters_id.create_results()

        return {
            'name': _('Analysis'),
            'domain': [('id', '=', new_analysis.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
            'target': 'current'
        }

    def open_analysis(self):
        return {
            'name': _('Analysis'),
            'domain': [('id', 'in', self.analysis_ids.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }

    def create_analysis_from_stock_move(self):
        self.ensure_one()
        stock_moves = self.picking_id.move_ids_without_package.filtered(lambda m: self.product_id in m.product_id)
        if 1 < len(stock_moves):
            raise exceptions.ValidationError(
                _("There are more than one stock's moves on the stock's picking using the product '{}'.".format(self.product_id.name))
            )
        laboratory = self.get_laboratory()
        category = self.get_category()
        analysis = stock_moves.move_line_ids.with_context(create_from_qc=True).create_analysis(
            laboratory=laboratory, customer_ref=self.name, category=category
        )
        self.analysis_ids += analysis
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_type': 'form',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('id', 'in', analysis.ids)],
        }
