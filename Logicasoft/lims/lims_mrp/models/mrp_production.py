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


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    rel_create_analysis = fields.Boolean(related='picking_type_id.create_analysis')
    nb_analysis = fields.Integer(compute='compute_nb_analysis', groups="lims_base.viewer_group")
    can_create_analysis = fields.Boolean(compute='compute_can_create_analysis')

    def get_analysis(self):
        analysis_ids = self.env['lims.analysis'].search([('customer_ref', '=', self.name)])
        return self.mapped('finished_move_line_ids.analysis_ids') + self.mapped(
            'move_raw_ids.move_line_ids.analysis_ids') + analysis_ids

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.get_analysis())

    def compute_can_create_analysis(self):
        for record in self:
            product_ok = record.product_id.lims_for_analysis and record.product_id.matrix_id
            record.can_create_analysis = record.rel_create_analysis and product_ok

    def create_analysis(self, lot_id=False, parameters_ids=False):
        """
        Create analysis from mrp.production, allow to add some specific lot and parameters (if possible)
        :param lot_id:
        :param parameters_ids:
        :return:
        """
        self.ensure_one()
        if not self.product_id:
            raise exceptions.ValidationError(_("No product inserted"))
        elif not self.product_id.lims_for_analysis:
            raise exceptions.ValidationError(_("Product is not configured for analysis"))
        elif not self.product_id.matrix_id:
            raise exceptions.ValidationError(_("Product have no matrix"))

        if not lot_id:
            lot_id = self.lot_producing_id
        pack_ids = self.product_id.additional_pack_ids or self.product_id.pack_ids

        if pack_ids:
            laboratory = pack_ids[0].labo_id
        else:
            laboratory = self.env['lims.laboratory'].sudo().search([('default_laboratory', '=', True)], limit=1)

        new_analysis = self.env['lims.analysis'].create({
            'product_id': self.product_id.id,
            'lot_id': lot_id.id,
            'date_plan': fields.Datetime.now(),
            'matrix_id': self.product_id.matrix_id.id,
            'customer_ref': self.name,
            'pack_ids': [(6, 0, pack_ids.ids)],
            'laboratory_id': laboratory.id
        })

        add_parameters_id = self.env['add.parameters.wizard'].create({
            'analysis_id': new_analysis.id
        })
        for pack_id in new_analysis.pack_ids:
            add_parameters_id.parameter_pack_id = pack_id
            add_parameters_id.create_line_from_pack(pack_id)
        add_parameters_id.create_results()

        if parameters_ids:
            for parameter_id in parameters_ids:
                current_parameters = new_analysis._get_all_method_param_charac()
                if parameter_id.active and parameter_id.state == 'validated' and parameter_id not in current_parameters:
                    add_parameters_id.method_param_charac_ids += parameter_id
                    current_parameters += parameter_id
                    add_parameters_id.onchange_parameter_characteristic_id()
            add_parameters_id.create_results()

        return self.open_new_analysis(new_analysis)

    def open_new_analysis(self, new_analysis):
        self.ensure_one()
        return {
            'name': _('Analysis'),
            'domain': [('id', '=', new_analysis.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current'
        }

    def open_analysis(self):
        self.ensure_one()
        analysis = self.get_analysis()
        return {
            'name': _('Analysis'),
            'domain': [('id', 'in', analysis.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }
