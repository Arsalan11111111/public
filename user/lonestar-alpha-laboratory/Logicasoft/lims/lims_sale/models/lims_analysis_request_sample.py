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
from odoo import models, fields


class LimsAnalysisRequestSample(models.Model):
    _inherit = 'lims.analysis.request.sample'

    sale_order_line_ids = fields.One2many('sale.order.line', 'sample_id', 'Sale Orders',
                                          domain=[('state', '!=', 'cancel')])
    rel_order_id = fields.Many2one('sale.order', related='request_id.order_id', store=True,
                                   help="This is the order of the request.")
    pack_invoiced_ids = fields.Many2many('lims.parameter.pack',
                                         'rel_request_sample_pack_invoiced', 'request_sample_id', 'pack_id',
                                         string='Packs invoiced',
                                         help='Pack that will only be invoiced, and not generate on the analyses',
                                         context={'active_test': False})

    pack_of_pack_invoiced_ids = fields.Many2many('lims.parameter.pack',
                                                 'rel_request_sample_pack_of_pack_invoiced', 'request_sample_id',
                                                 'pack_id',
                                                 string='Packs of packs invoiced',
                                                 help='Pack that will only be invoiced, and not generate on the '
                                                      'analyses',
                                                 context={'active_test': False})
    allow_additional_pack_invoiced = fields.Boolean(compute='get_allow_additional_pack_invoiced')

    def update_parameter_vals(self, vals, section_name, product, parameter_ids=None, add_parameters=None):
        """

        :param vals:
        :param section_name:
        :param product:
        :param parameter_ids:
        :param add_parameters:
        :return:
        """
        if section_name not in vals:
            vals[section_name] = {}

        if product not in vals[section_name]:
            vals[section_name][product] = {}

        if 'quantity' in vals[section_name][product]:
            vals[section_name][product]['quantity'] += 1
        else:
            vals[section_name][product]['quantity'] = 1

        if add_parameters:
            if 'parameter_ids' not in vals[section_name][product]:
                vals[section_name][product]['parameter_ids'] = []
            vals[section_name][product]['parameter_ids'] += [(4, parameter.id) for parameter in parameter_ids]
        else:
            vals[section_name][product]['parameter_ids'] = [(6, 0, parameter_ids.ids)] if parameter_ids else False

        vals[section_name][product]['sample_id'] = self.id if (
                self.env.context.get('section_model') == 'lims_analysis_request_sample'
        ) else False

    def _get_invoiceable_parameters(self):
        additional = bool(self.env['ir.config_parameter'].sudo().get_param('lims_sale.additional_pack_invoiced', False))
        vals = {}
        for record in self:
            parameters_in_so = []
            lang = record.request_id.partner_id.lang
            pack_of_pack_ids = record.pack_of_pack_ids.filtered(lambda p: p.billable)
            # Fonction additional items to invoice:
            additional_pack_of_packs = additional and record._get_pack_of_pack_invoiced_ids(pack_of_pack_ids)
            if additional_pack_of_packs:
                pack_of_pack_ids += additional_pack_of_packs
            for pack_of_pack_id in pack_of_pack_ids:
                parameter_ids = pack_of_pack_id.pack_of_pack_ids.pack_id.parameter_ids.method_param_charac_id
                parameters_in_so += parameter_ids.ids
                pack_of_pack_id = pack_of_pack_id.with_context(lang=lang)
                pack_name = pack_of_pack_id.so_section_name or pack_of_pack_id.name
                product_id = pack_of_pack_id.get_product(sample_id=record)
                if product_id:
                    parameter_ids = additional and pack_of_pack_id in additional_pack_of_packs and parameter_ids.filtered(
                                lambda p: p in record.method_param_charac_ids) or parameter_ids
                    record.update_parameter_vals(vals, pack_name, product_id, parameter_ids, add_parameters=True)
            pack_ids = record.pack_ids.filtered(lambda p: p.id not in pack_of_pack_ids.pack_of_pack_ids.pack_id.ids)
            # Fonction additional items to invoice:
            additional_packs = additional and record._get_pack_invoiced_ids(pack_ids, pack_of_pack_ids)
            if additional_packs:
                pack_ids += additional_packs
            for pack_id in pack_ids:
                pack_id = pack_id.with_context(lang=lang)
                pack_name = pack_id.so_section_name or pack_id.name
                product_id = pack_id.get_product(sample_id=record)
                if pack_id.billable and product_id:
                    parameter_ids = pack_id.parameter_ids.method_param_charac_id
                    parameters_in_so += parameter_ids.ids
                    parameter_ids = additional and pack_id in additional_packs and parameter_ids.filtered(
                        lambda p: p in record.method_param_charac_ids) or parameter_ids
                    record.update_parameter_vals(vals, pack_name, product_id, parameter_ids, add_parameters=True)
                else:
                    for parameter_id in pack_id.parameter_ids.method_param_charac_id:
                        product_id = parameter_id.get_product(sample_id=record)
                        if parameter_id.billable and product_id and parameter_id.id not in parameters_in_so:
                            record.update_parameter_vals(vals, pack_name, product_id, parameter_id, add_parameters=True)
                            parameters_in_so.append(parameter_id.id)
            method_param_charac_ids = record.method_param_charac_ids.filtered(
                lambda
                    p: p not in record.pack_ids.parameter_ids.method_param_charac_id and p.id not in parameters_in_so)
            for parameter_id in method_param_charac_ids:
                product_id = parameter_id.get_product(sample_id=record)
                if parameter_id.billable and product_id:
                    record.update_parameter_vals(vals, parameter_id.tech_name, product_id, parameter_id,
                                                 add_parameters=True)
        return vals

    def _get_pack_of_pack_invoiced_ids(self, pack_of_pack_ids):
        self.ensure_one()
        return self.pack_of_pack_invoiced_ids.filtered(lambda p: p.billable and p.id not in pack_of_pack_ids.ids)

    def _get_pack_invoiced_ids(self, pack_ids, pack_of_pack_ids):
        self.ensure_one()
        return self.pack_invoiced_ids.filtered(
            lambda p: lambda p: p.id not in pack_of_pack_ids.pack_of_pack_ids.pack_id.ids and p.id not in pack_ids.ids)

    def get_allow_additional_pack_invoiced(self):
        config = bool(self.env['ir.config_parameter'].sudo().get_param('lims_sale.additional_pack_invoiced', False))
        for record in self:
            record.allow_additional_pack_invoiced = config
        return config
