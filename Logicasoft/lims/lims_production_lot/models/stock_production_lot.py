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


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    nb_analysis = fields.Integer(compute='compute_info_analysis')
    nb_result = fields.Integer(compute='compute_info_analysis')
    nb_compute_result = fields.Integer(compute='compute_info_analysis')
    nb_sel_result = fields.Integer(compute='compute_info_analysis')
    nb_text_result = fields.Integer(compute='compute_info_analysis')
    rel_lims_for_analysis = fields.Boolean(related='product_id.lims_for_analysis')

    def compute_info_analysis(self):
        for record in self:
            analysis = self.env['lims.analysis'].search([('lot_id', '=', record.id)])
            record.update({
                'nb_analysis': len(analysis),
                'nb_result': len(analysis.result_num_ids),
                'nb_compute_result': len(analysis.result_compute_ids),
                'nb_sel_result': len(analysis.result_sel_ids),
                'nb_text_result': len(analysis.result_text_ids),
            })

    def get_all_analysis_view(self):
        return {
            'name': _('Analysis'),
            'domain': [('lot_id', '=', self.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }

    def get_all_analysis_result_view(self):
        analysis_ids = self.env['lims.analysis'].search([('lot_id', '=', self.id)])
        return {
            'name': _('Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_sel_result_view(self):
        analysis_ids = self.env['lims.analysis'].search([('lot_id', '=', self.id)])
        return {
            'name': _('Sel Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_compute_result_view(self):
        analysis_ids = self.env['lims.analysis'].search([('lot_id', '=', self.id)])
        return {
            'name': _('Compute Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
            'view_type': 'form',
        }

    def get_all_analysis_text_result_view(self):
        analysis_ids = self.env['lims.analysis'].search([('lot_id', '=', self.id)])
        return {
            'name': _('Text Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def create_analysis(self):
        analysis_obj = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']
        laboratory_obj = self.env['lims.laboratory']
        default_laboratory = laboratory_obj.sudo().search([('default_laboratory', '=', True)])

        # product_id is a required field
        unchecks = self.filtered(lambda lot: not lot.product_id.lims_for_analysis)
        if unchecks:
            name_product_format = [lot.name +' / '+ lot.product_id.name  for lot in unchecks]
            errorMessage = _("Products involved in that lots/Serial Numbers have the boolean 'lims_for_analysis' uncheck : \n{}".format('\n'.join(name_product_format)))
            raise exceptions.UserError(errorMessage)
        if self.filtered(lambda lot: not lot.product_id.matrix_id):
            raise exceptions.UserError(_("Some products have no matrix."))
        ids = []
        for record in self:
            laboratory_id = laboratory_obj.search([('company_id', '=', record.company_id.id)], limit=1)
            if not laboratory_id:
                laboratory_id = default_laboratory

            pack_ids = record.product_id.additional_pack_ids or record.product_id.pack_ids
            new_analysis = analysis_obj.create({
                'product_id': record.product_id.id,
                'lot_id': record.id,
                'date_plan': fields.Datetime.now(),
                'date_sample': fields.Datetime.now(),
                'date_sample_receipt': fields.Datetime.now(),
                'matrix_id': record.product_id.matrix_id.id,
                'pack_ids': [(6, 0, pack_ids.ids)],
                'laboratory_id': laboratory_id.id,
                'category_id': laboratory_id.default_request_category_id.id
            })
            new_analysis.do_plan()

            ids.append(new_analysis.id)
            # copy from stock_move.py in lims_inventory
            add_parameters_id = add_parameters_obj.create({
                'analysis_id': new_analysis.id
            })
            for pack_id in new_analysis.pack_ids:
                add_parameters_id.parameter_pack_id = pack_id
                add_parameters_id.create_line_from_pack(pack_id)
            add_parameters_id.create_results()

        return {
            'name': 'Analysis',
            'domain': [('id', 'in', ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
            'target': 'current'
        }
