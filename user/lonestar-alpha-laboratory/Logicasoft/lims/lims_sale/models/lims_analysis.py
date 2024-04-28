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


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    order_id = fields.Char('Ref PO')
    sale_order_id = fields.Many2one('sale.order', 'Order', copy=False,
                                    groups="sales_team.group_sale_salesman,base.group_portal",
                                    help="The most recent sale order linked with this analysis.")
    costing_ids = fields.One2many('lims.analysis.costing', 'analysis_id', string='Costing',
                                  groups="sales_team.group_sale_salesman")
    total_cost = fields.Float(compute='compute_total', string='Total Cost', store=True,
                              groups="sales_team.group_sale_salesman",
                              help="Sum of the cost multiplied by the quantity for each costing line.")
    total_revenue = fields.Float(compute='compute_total', string='Total Revenue', store=True,
                                 groups="sales_team.group_sale_salesman",
                                 help="Sum of the revenue multiplied by the quantity for each costing line.")
    rel_currency_id = fields.Many2one('res.currency', related='laboratory_id.company_id.currency_id', compute_sudo=True,
                                      help="This is the currency present in the company of the laboratory.")
    display_warning = fields.Boolean()
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',
                                   help="If the analysis comes from a request, the price list will be linked to the "
                                        "request. Otherwise, the default price list will be the one defined for the "
                                        "customer; in this case the price list can be modified if the analysis is not "
                                        "indicated as 'to do'")
    pack_invoiced_ids = fields.Many2many('lims.parameter.pack',
                                         'rel_analysis_pack_invoiced', 'analysis_id', 'pack_id',
                                         string='Packs invoiced',
                                         help='Pack that will only be invoiced, and not generate on the analyses',
                                         context={'active_test': False})

    pack_of_pack_invoiced_ids = fields.Many2many('lims.parameter.pack',
                                                 'rel_analysis_pack_of_pack_invoiced', 'analysis_id',
                                                 'pack_id',
                                                 string='Packs of packs invoiced',
                                                 help='Pack that will only be invoiced, and not generate on the '
                                                      'analyses',
                                                 context={'active_test': False})
    allow_additional_pack_invoiced = fields.Boolean(compute='get_allow_additional_pack_invoiced')

    def action_create_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.create.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_ids': self.ids}
        }

    def create_sale_order(self):
        if self.filtered(lambda r: not r.pricelist_id):
            raise exceptions.ValidationError(_('There is no pricelist set in at least one analysis'))

        if self.filtered(lambda r: not r.laboratory_id):
            raise exceptions.ValidationError(_("One of your analysis don't have a laboratory"))

        partner_ids = self.mapped('partner_id')
        sale_order_ids = self.env['sale.order']
        vals = {'date_order': fields.Datetime.now(), 'state': 'draft'}
        for partner_id in partner_ids:
            sale_vals = vals.copy()
            analysis_ids = self.filtered(lambda a: a.partner_id == partner_id)
            if analysis_ids.filtered(lambda a: a.sale_order_id):
                analysis_ids.mapped('sale_order_id').action_cancel()

            if len(analysis_ids.mapped('pricelist_id')) > 1:
                raise exceptions.ValidationError(_("You can't make a sale order with analysis with "
                                                   "different pricelists"))

            if len(analysis_ids.mapped('laboratory_id')) > 1:
                raise exceptions.ValidationError(_("You can't make a sale order with analysis from different "
                                                   "laboratories"))

            pricelist_id = analysis_ids[0].pricelist_id
            laboratory_id = analysis_ids[0].laboratory_id
            sale_vals.update({
                'partner_id': partner_id.id,
                'pricelist_id': pricelist_id.id,
                'analysis_ids': [(6, 0, analysis_ids.ids)],
                'company_id': laboratory_id.company_id.id
            })
            if self.env.context.get('order_template'):
                sale_vals.update({
                    'sale_order_template_id': self.env.context.get('order_template'),
                })
            sale_order_id = self.env['sale.order'].create(sale_vals)

            sale_order_ids += sale_order_id
            section_model = self.env.context.get('section_model') or laboratory_id.section_model
            analysis_ids.create_so_line(sale_order_id, section_model)

        action = self.env['ir.actions.act_window']._for_xml_id('lims_sale.lims_action_quotation_tree')
        action['domain'] = [('id', 'in', sale_order_ids.ids)]
        return action

    def create_so_line(self, sale_order_id, section_model):
        """
        Create so lines according to different logics
        Code is not in the main method to allow inheritance of creating logic
        :param sale_order_id: SO already created
        :param laboratory_id: laboratory
        :return: None
        """
        if len(self) > 1 or section_model == 'lims_analysis_request_sample':
            self.create_so_line_grouped_analysis(sale_order_id)
        elif section_model == 'lims_parameter_pack':
            self.create_so_line_pack(sale_order_id)

    def create_so_line_grouped_analysis(self, sale_order_id):
        for record in self:
            self.env['sale.order.line'].create({
                'name': record.name,
                'order_id': sale_order_id.id,
                'request_id': record.request_id.id or False,
                'display_type': 'line_section',
                'state': 'cancel',
                'sequence': len(sale_order_id.order_line) + 1
            })
            record.with_context(no_section=True).create_so_line_pack(sale_order_id)

    def create_so_line_pack(self, sale_order_id):
        pack_ids = self.costing_ids.mapped('pack_ids')
        method_param_charac_ids = self.costing_ids.filtered(lambda c: not c.pack_ids).mapped('method_param_charac_ids')

        for pack_id in pack_ids:
            if not self.env.context.get('no_section'):
                self.env['sale.order.line'].create({
                    'name': pack_id.with_context(lang=self.partner_id.lang).name,
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'display_type': 'line_section',
                    'state': 'cancel',
                    'sequence': len(sale_order_id.order_line) + 1
                })
            for costing_id in self.costing_ids.filtered(lambda c: pack_id in c.pack_ids):
                if not costing_id.product_id or not costing_id.product_id.active:
                    raise exceptions.MissingError(
                        _("Costing line has either no product or its product is deactivated. "
                          "Reactivate or change product in order to create a sale order"))

                parameters_ids = pack_id.mapped('pack_of_pack_ids.pack_id.parameter_ids.method_param_charac_id') \
                    if pack_id.is_pack_of_pack else pack_id.parameter_ids.mapped('method_param_charac_id')

                if costing_id.method_param_charac_ids:
                    parameters_ids = costing_id.method_param_charac_ids

                self.env['sale.order.line'].create({
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'product_id': costing_id.product_id.id,
                    'product_uom': costing_id.product_id.uom_id.id,
                    'product_uom_qty': costing_id.qty,
                    'price_unit': costing_id.revenue,
                    'parameter_ids': [(6, 0, parameters_ids.ids)],
                    'sequence': len(sale_order_id.order_line) + 1
                })

        for method_param_charac_id in method_param_charac_ids:
            if not self.env.context.get('no_section'):
                self.env['sale.order.line'].create({
                    'name': method_param_charac_id.name,
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'display_type': 'line_section',
                    'state': 'cancel',
                    'sequence': len(sale_order_id.order_line) + 1
                })
            for costing_id in self.costing_ids.filtered(
                    lambda c: method_param_charac_id in c.method_param_charac_ids):
                self.env['sale.order.line'].create({
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'product_id': costing_id.product_id.id,
                    'product_uom': costing_id.product_id.uom_id.id,
                    'product_uom_qty': costing_id.qty,
                    'price_unit': costing_id.revenue,
                    'parameter_ids': [(6, 0, [method_param_charac_id.id])],
                    'sequence': len(sale_order_id.order_line) + 1
                })

        costing_ids = self.costing_ids.filtered(lambda c: not c.pack_ids and not c.method_param_charac_ids)
        if costing_ids:
            if not self.env.context.get('no_section'):
                self.env['sale.order.line'].create({
                    'name': _('Individuals articles'),
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'display_type': 'line_section',
                    'state': 'cancel',
                    'sequence': len(sale_order_id.order_line) + 1
                })
            for costing_id in costing_ids:
                self.env['sale.order.line'].create({
                    'order_id': sale_order_id.id,
                    'request_id': self.request_id.id or False,
                    'product_id': costing_id.product_id.id,
                    'product_uom': costing_id.product_id.uom_id.id,
                    'product_uom_qty': costing_id.qty,
                    'price_unit': costing_id.revenue,
                    'parameter_ids': False,
                    'sequence': len(sale_order_id.order_line) + 1
                })

    @api.depends('costing_ids')
    def compute_total(self):
        for record in self:
            record.total_cost = sum(costing_id.cost * costing_id.qty for costing_id in record.costing_ids)
            record.total_revenue = sum(costing_id.revenue * costing_id.qty for costing_id in record.costing_ids)

    def compute_pack(self, pack):
        if not pack.billable:
            if pack.is_pack_of_pack:
                for subpack in pack.pack_of_pack_ids.mapped('pack_id'):
                    if subpack not in self.costing_ids.mapped('pack_ids'):
                        self.compute_pack(subpack)
            else:
                param_ids = pack.parameter_ids.mapped('method_param_charac_id')
                self.compute_param(param_ids, fromPack=pack)
        else:
            product_id = pack.get_product(analysis_id=self)
            if product_id and pack not in self.costing_ids.mapped('pack_ids'):
                if product_id not in self.costing_ids.mapped('product_id'):
                    final_price = product_id.list_price
                    if self.pricelist_id:
                        final_price_and_rule = self.pricelist_id._get_product_price_rule(product_id, 1.0)
                        final_price = final_price_and_rule[0]
                    self.costing_ids.create({
                        'product_id': product_id.id,
                        'analysis_id': self.id,
                        'cost': product_id.standard_price,
                        'revenue': final_price,
                        'pack_ids': [(6, 0, [pack.id])],
                    })
                else:
                    costing = self.costing_ids.filtered(lambda c: c.product_id == product_id)[0]
                    costing.qty += 1
                    costing.pack_ids += pack

    def compute_param(self, method_param_ids, fromPack=False):
        for method_param in method_param_ids.filtered(
                lambda p: p.billable or p.parameter_id.product_id):
            product_id = method_param.get_product(analysis_id=self)
            if product_id and product_id not in self.costing_ids.mapped('product_id'):
                final_price = product_id.list_price
                if self.pricelist_id:
                    final_price_and_rule = self.pricelist_id._get_product_price_rule(product_id, 1.0)
                    final_price = final_price_and_rule[0]
                self.costing_ids.create({
                    'product_id': product_id.id,
                    'analysis_id': self.id,
                    'cost': product_id.standard_price,
                    'revenue': final_price,
                    'pack_ids': [(6, 0, [fromPack.id])] if fromPack else False,
                    'method_param_charac_ids': [(6, 0, method_param.ids)],
                })
            elif product_id:
                costing = self.costing_ids.filtered(lambda c: c.product_id == product_id)[0]
                costing.qty += 1
                costing.method_param_charac_ids += method_param

    def compute_costing(self):
        for record in self:
            individuals_articles_costing_ids = record.costing_ids.filtered(lambda c: not c.method_param_charac_ids and not c.pack_ids)
            record.costing_ids = [(6, 0, individuals_articles_costing_ids.ids)]

            all_packs = record.pack_ids | record.pack_of_pack_ids
            parent_pack = all_packs.filtered('is_pack_of_pack')

            if parent_pack:
                removed_child_pack_ids = self.env['lims.parameter.pack'].browse([])
                for pack_id in all_packs.filtered(lambda p: not p.is_pack_of_pack):
                    if pack_id in parent_pack.filtered("billable").mapped('pack_of_pack_ids').mapped('pack_id'):
                        removed_child_pack_ids += pack_id
                all_packs -= removed_child_pack_ids

            for pack in all_packs:
                record.compute_pack(pack)

            record.compute_param(record.method_param_charac_ids)

        self.compute_total()

    def get_vals_for_recurrence(self):
        vals = super(LimsAnalysis, self).get_vals_for_recurrence()
        vals['order_id'] = ''
        return vals

    def create_sale_order_wizard(self):
        if len(self.mapped('partner_id')) > 1:
            raise exceptions.ValidationError(_('Only one client must be present into that selection'))
        return {
            'name': _('Confirm create sale order'),
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.create.order.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_ids': self.ids},
        }

    @api.onchange('partner_id')
    def onchange_partner_id_pricelist_id(self):
        for record in self.filtered(lambda a: (not a.request_id) and (a.rel_type in ['draft', 'plan'])):
            record.pricelist_id = record.partner_id.property_product_pricelist.id

    @api.onchange('pricelist_id')
    def onchange_pricelist_id_costing_ids(self):
        for record in self:
            if record.sale_order_id:
                record.display_warning = True
            for costing_id in record.costing_ids.filtered("product_id"):
                final_price = costing_id.product_id.list_price
                if record.pricelist_id:
                    final_price_and_rule = record.pricelist_id._get_product_price_rule(costing_id.product_id, 1.0)
                    final_price = final_price_and_rule[0]
                costing_id.cost = costing_id.product_id.standard_price * costing_id.qty
                costing_id.revenue = final_price * costing_id.qty

    def get_allow_additional_pack_invoiced(self):
        config = bool(self.env['ir.config_parameter'].sudo().get_param('lims_sale.additional_pack_invoiced', False))
        for record in self:
            record.allow_additional_pack_invoiced = config
        return config

    def get_portal_order_id(self):
        self.ensure_one()
        order_id = False
        try:
            order_id = self.order_id
        finally:
            return order_id
