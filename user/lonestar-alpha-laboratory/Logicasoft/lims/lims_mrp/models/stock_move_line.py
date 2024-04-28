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

    def get_vals_analysis(self):
        vals = super().get_vals_analysis()
        if not vals.get('date_plan', False):
            vals['date_plan'] = fields.Datetime.now()
        if not vals.get('date_sample', False):
            vals['date_sample'] = fields.Datetime.now()
        if not vals.get('date_sample_receipt', False):
            vals['date_sample_receipt'] = fields.Datetime.now()
        return vals

    def create_analysis_mrp(self):
        if self.filtered(lambda s: not s.product_id):
            raise exceptions.ValidationError(_("No product inserted"))
        elif self.filtered(lambda s: not s.product_id.lims_for_analysis):
            raise exceptions.ValidationError(_("Product have boolean 'Lims For Analysis' uncheck"))
        elif self.filtered(lambda s: not s.product_id.matrix_id):
            raise exceptions.ValidationError(_("Product have no matrix"))

        analysis_ids = self.env['lims.analysis']
        add_parameters_obj = self.env['add.parameters.wizard']
        for record in self:
            vals = record.get_vals_analysis()
            if 'laboratory_id' not in vals:
                raise exceptions.ValidationError(_('No laboratory found for this company.'))

            context = record.env.context.copy()
            # default state : 'draft' (trigger an error)
            if context.get('default_state'):
                del context['default_state']
            # default_location: location_src_id(stock.location)
            # try to fill location_id(lims.sampling.point.location)
            # Not the same model
            if context.get('default_location_id'):
                del context['default_location_id']

            analysis = analysis_ids.with_context(context).create(vals)
            analysis.do_plan()

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
