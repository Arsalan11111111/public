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

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.analysis_ids)

    def create_analysis(self, lot=False):
        self.ensure_one()
        if not self.product_id:
            raise exceptions.ValidationError(_("No product inserted"))
        elif not self.product_id.lims_for_analysis:
            raise exceptions.ValidationError(_("Product have boolean 'lims_for_analysis' uncheck"))
        elif not self.product_id.matrix_id:
            raise exceptions.ValidationError(_("Product have no matrix"))
        elif not self.point_id.create_analysis:
            raise exceptions.ValidationError(_("The 'Create analysis' boolean is unchecked on control point."))

        analysis_obj = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']

        pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids

        if pack_ids:
            laboratory = pack_ids[0].labo_id
        else:
            laboratory = self.env['lims.laboratory'].sudo().search([('default_laboratory', '=', True)], limit=1)

        new_analysis = analysis_obj.create({
            'product_id': self.product_id.id,
            'lot_id': lot.id if lot else self.lot_id.id,
            'date_plan': fields.Datetime.now(),
            'date_sample': fields.Datetime.now(),
            'matrix_id': self.product_id.matrix_id.id,
            'customer_ref': self.name,
            'pack_ids': [(6, 0, pack_ids.ids)],
            'laboratory_id': laboratory.id,
            'category_id': self.point_id.analysis_category_id.id
        })
        self.analysis_ids = [(4, new_analysis.id)]
        # copy from stock_move.py in lims_inventory
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
        self.ensure_one()
        return {
            'name': _('Analysis'),
            'domain': [('id', '=', self.analysis_ids.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }

    def create_analysis_from_stock_move(self):
        self.ensure_one()
        if not self.analysis_ids.filtered(lambda a: a.rel_type != 'cancel'):
            return self.picking_id.move_ids_without_package.create_analysis()
        raise exceptions.UserError(_("There are at least one analysis linked to that quality control that is not cancelled."))