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


class StockLot(models.Model):
    _inherit = 'stock.lot'

    analysis_ids = fields.One2many('lims.analysis', 'lot_id')
    nb_analysis = fields.Integer(compute='compute_info_analysis')
    nb_result = fields.Integer(compute='compute_info_analysis')
    nb_compute_result = fields.Integer(compute='compute_info_analysis')
    nb_sel_result = fields.Integer(compute='compute_info_analysis')
    nb_text_result = fields.Integer(compute='compute_info_analysis')
    rel_lims_for_analysis = fields.Boolean(related='product_id.lims_for_analysis')

    def compute_info_analysis(self):
        for record in self:
            record.update({
                'nb_analysis': len(record.analysis_ids),
                'nb_result': len(record.analysis_ids.result_num_ids),
                'nb_compute_result': len(record.analysis_ids.result_compute_ids),
                'nb_sel_result': len(record.analysis_ids.result_sel_ids),
                'nb_text_result': len(record.analysis_ids.result_text_ids),
            })

    def get_all_analysis_view(self):
        return {
            'name': _('Analysis'),
            'domain': [('lot_id', 'in', self.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }

    def get_all_analysis_result_view(self):
        return {
            'name': _('Result'),
            'domain': [('analysis_id.lot_id', 'in', self.ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_sel_result_view(self):
        return {
            'name': _('Sel Result'),
            'domain': [('analysis_id.lot_id', 'in', self.ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_compute_result_view(self):
        return {
            'name': _('Compute Result'),
            'domain': [('analysis_id.lot_id', 'in', self.ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_text_result_view(self):
        return {
            'name': _('Text Result'),
            'domain': [('analysis_id.lot_id', 'in', self.ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def create_analysis(self):
        if self.filtered(lambda l: not l.product_id):
            raise exceptions.ValidationError(_("No product inserted"))
        elif self.filtered(lambda l: not l.product_id.lims_for_analysis):
            raise exceptions.ValidationError(_("Product have boolean 'Lims For Analysis' uncheck"))
        elif self.filtered(lambda l: not l.product_id.matrix_id):
            raise exceptions.ValidationError(_("Product have no matrix"))

        analysis_obj = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']
        laboratory_obj = self.env['lims.laboratory']
        default_laboratory = laboratory_obj.sudo().search([('default_laboratory', '=', True)], limit=1)

        ids = []
        for record in self:
            laboratory = record.product_id.pack_ids[0].labo_id if record.product_id.pack_ids else False
            if not laboratory:
                laboratory = laboratory_obj.sudo().search([('company_id', '=', record.company_id.id)], limit=1)
            if not laboratory:
                laboratory = default_laboratory

            pack_ids = record.product_id.additional_pack_ids or record.product_id.pack_ids
            new_analysis = analysis_obj.create({
                'product_id': record.product_id.id,
                'lot_id': record.id,
                'date_plan': fields.Datetime.now(),
                'date_sample': fields.Datetime.now(),
                'date_sample_receipt': fields.Datetime.now(),
                'matrix_id': record.product_id.matrix_id.id,
                'pack_ids': [(6, 0, pack_ids.ids)],
                'laboratory_id': laboratory.id if laboratory else False,
                'category_id': laboratory.default_request_category_id.id if laboratory else False
            })
            new_analysis.do_plan()

            ids.append(new_analysis.id)
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
            'domain': [('id', 'in', ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
            'target': 'current'
        }
