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


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    analysis_ids = fields.Many2many('lims.analysis', string="Analysis")
    rel_lims_for_analysis = fields.Boolean(related='product_id.lims_for_analysis')
    lock_button = fields.Boolean(compute='compute_lock_button')

    def get_analysis_for_lock_button(self):
        return self.analysis_ids.filtered(lambda a: a.rel_type != 'cancel')

    @api.depends('analysis_ids')
    def compute_lock_button(self):
        for record in self:
            lock_button = False
            if record.get_analysis_for_lock_button():
                lock_button = True
            record.lock_button = lock_button

    def get_laboratory(self):
        self.ensure_one()
        pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids
        laboratory = pack_ids[0].labo_id if pack_ids else False
        if not laboratory:
            laboratory = self.picking_type_id.laboratory_company_id
        if not laboratory:
            laboratory = self.env['lims.laboratory'].sudo().search([('company_id', '=', self.picking_id.company_id.id)], limit=1)
        if not laboratory:
            laboratory = self.env['lims.laboratory'].sudo().search([('default_laboratory', '=', True)], limit=1)
        return laboratory

    def get_category(self):
        self.ensure_one()
        category = self.picking_type_id.analysis_category_id
        if not category:
            laboratory = self.get_laboratory()
            category = laboratory.default_analysis_category_id if laboratory else False
        return category

    def get_vals_analysis(self):
        self.ensure_one()
        laboratory = self.get_laboratory()
        category = self.get_category()
        return {
            'product_id': self.product_id.id,
            'matrix_id': self.product_id.matrix_id.id,
            'lot_id': self.lot_id.id,
            'customer_ref': self.reference,
            'date_plan': self.date,
            'category_id': category.id if category else False,
            'laboratory_id': laboratory.id if laboratory else False,
            'date_sample_begin': fields.Datetime.now()
        }

    def create_analysis(self, laboratory=False, lot=False, nbr=1, customer_ref=False, category=False):
        if self.filtered(lambda s: not s.product_id):
            raise exceptions.ValidationError(_("No product inserted"))
        elif self.filtered(lambda s: not s.product_id.lims_for_analysis):
            raise exceptions.ValidationError(_("Product have boolean 'Lims For Analysis' uncheck"))
        elif self.filtered(lambda s: not s.product_id.matrix_id):
            raise exceptions.ValidationError(_("Product have no matrix"))

        analysis_ids = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']
        for record in self.filtered(lambda ml: ml.picking_id):
            if record.picking_id.state not in ['assigned', 'done']:
                raise exceptions.ValidationError(_("Picking should be at least 'Ready'."))

            vals = record.get_vals_analysis()

            if not (laboratory or ('laboratory_id' in vals)):
                raise exceptions.ValidationError(_('No laboratory found for this company.'))

            if laboratory:
                vals['laboratory_id'] = laboratory.id
            if lot:
                vals['lot_id'] = lot.id
            if customer_ref:
                vals['customer_ref'] = customer_ref
            if category:
                vals['category_id'] = category.id

            context = self.env.context.copy()
            # default state : 'draft' (trigger an error)
            if context.get('default_state'):
                del context['default_state']
            # default_location: location_src_id(stock.location)
            # try to fill location_id(lims.sampling.point.location)
            # Not the same model
            if context.get('default_location_id'):
                del context['default_location_id']

            for i in range(nbr):
                analysis = analysis_ids.with_context(context).create(vals)
                add_parameters_id = add_parameters_obj.create({
                    'analysis_id': analysis.id
                })
                pack_ids = record.product_id.additional_pack_ids or record.product_id.pack_ids
                for pack_id in pack_ids:
                    add_parameters_id.parameter_pack_id = pack_id
                    add_parameters_id.create_line_from_pack(pack_id)
                add_parameters_id.with_context(context).create_results()
                record.analysis_ids += analysis
                analysis_ids += analysis

        return analysis_ids
