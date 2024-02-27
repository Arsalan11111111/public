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
from odoo import fields, models, api, exceptions, Command, _


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',
                                   help="It helps to defined specific prices for products. "
                                        "If you changes the client, his pricelist will take over.")
    order_id = fields.Many2one('sale.order', 'Sale order', readonly=True, copy=False,
                               groups="sales_team.group_sale_salesman,base.group_portal")
    amount_untaxed = fields.Float('Amount Untaxed', compute='compute_amount_untaxed', readonly=True, store=True,
                                  groups="sales_team.group_sale_salesman",
                                  help="This is the amount untaxed of the order.")
    display_warning = fields.Boolean()
    invoice_count = fields.Integer(string='Invoice(s)', compute='count_invoices', store=True,
                                   groups="sales_team.group_sale_salesman")
    invoice_to_id = fields.Many2one('res.partner', string='Quotation/invoice Contact', tracking=True,
                                    help="It will be the customer of the order.")
    sale_order_count = fields.Integer(string='Sale order count', compute='compute_sale_order_count')

    @api.onchange('partner_id')
    def onchange_invoice_to(self):
        for record in self.filtered(lambda r: not r.invoice_to_id):
            record.invoice_to_id = record.partner_id

    def compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = self.env['sale.order'].search_count([
                '|', ('analysis_request_id', '=', record.id), ('analysis_request_ids', 'in', [record.id])
            ])

    def do_cancel(self):
        super(LimsAnalysisRequest, self).do_cancel()
        for record in self.filtered(lambda r: r.order_id and r.order_id.invoice_status == 'to invoice'):
            record.order_id.with_context(disable_cancel_warning=True).action_cancel()

    @api.depends('order_id', 'order_id.invoice_ids')
    def count_invoices(self):
        for record in self:
            order_ids = self.get_all_sale_orders()
            record.invoice_count = len(order_ids.invoice_ids)

    @api.depends('order_id', 'order_id.amount_untaxed')
    def compute_amount_untaxed(self):
        for record in self.filtered(lambda r: r.order_id):
            record.amount_untaxed = record.order_id.amount_untaxed

    @api.onchange('partner_id')
    def onchange_partner(self):
        for record in self:
            record.pricelist_id = record.partner_id.property_product_pricelist

    def create_analysis(self, reception_date, sample_and_due_date, sample_ids=None):
        res = super().create_analysis(reception_date, sample_and_due_date, sample_ids=sample_ids)
        if self.order_id:
            self.analysis_ids.write({
                'sale_order_id': self.order_id.id
            })
        self.analysis_ids.compute_costing()
        return res

    def add_analysis_values(self, sample_id, sample_info=False):
        res = super().add_analysis_values(sample_id, sample_info=sample_info)
        res.update({
            'pricelist_id': self.pricelist_id.id
        })
        if sample_id:
            res.update({
                'pack_invoiced_ids': [(4, pack_id.id) for pack_id in sample_id.pack_invoiced_ids],
                'pack_of_pack_invoiced_ids': [(4, pack_id.id) for pack_id in sample_id.pack_of_pack_invoiced_ids],
            })
        return res

    def create_sale_order(self):
        self.ensure_one()
        if not self.invoice_to_id:
            raise exceptions.ValidationError(_('There is no quotation/invoice contact in the request'))
        if self.labo_id.company_id != self.env.user.company_id:
            raise exceptions.ValidationError(_('You can not create a quotation for another company'))
        if not self.pricelist_id:
            raise exceptions.ValidationError(_('There is no pricelist set in the request'))
        if self.order_id:
            self.get_all_sale_orders().with_context(disable_cancel_warning=True).action_cancel()
        if self.analysis_ids.filtered(lambda a: a.sale_order_id):
            self.analysis_ids.mapped('sale_order_id').action_cancel()
        order_vals = {
            'partner_id': self.invoice_to_id.id,
            'user_id': self.salesperson.id or self.env.uid,
            'pricelist_id': self.pricelist_id.id,
            'client_order_ref': self.customer_order_ref,
            'customer_ref': self.customer_ref,
            'partner_contact_ids': [(4, partner_contact_id.id) for partner_contact_id in self.partner_contact_ids],
            'analysis_request_id': self.id,
            'analysis_request_ids': [Command.link(self.id)],
            'analysis_ids': [Command.set(self.analysis_ids.ids)],
            'company_id': self.labo_id.company_id.id
        }
        if self.env.context.get('order_template'):
            order_vals.update({
                'sale_order_template_id': self.env.context.get('order_template')
            })
        ctx_vals = self.env.context.get('order_vals')
        if ctx_vals and type(ctx_vals) == dict:
            order_vals.update(
                self.env.context.get('order_vals')
            )
        order_id = self.env['sale.order'].create(order_vals)
        order_id._onchange_sale_order_template_id()
        self.order_id = order_id
        laboratory_id = self.labo_id
        section_model = self.env.context.get('section_model') or laboratory_id.section_model
        line_vals = self._prepare_sale_order(section_model)
        order_line_obj = self.env['sale.order.line']
        for line_val in line_vals:
            order_line_obj.create({
                'name': self.get_line_section_name(line_val),
                'order_id': order_id.id,
                'request_id': self.id,
                'display_type': 'line_section',
            })
            for product_id in line_vals[line_val]:
                product_vals = line_vals[line_val][product_id]
                order_line_obj.create({
                    'product_id': product_id.id,
                    'product_uom': product_id.uom_id.id,
                    'product_uom_qty': product_vals.get('quantity'),
                    'parameter_ids': product_vals.get('parameter_ids'),
                    'sample_id': product_vals.get('sample_id'),
                    'order_id': order_id.id,
                    'request_id': self.id,
                })
        form = self.env.ref('sale.view_order_form')
        action = self.env['ir.actions.act_window']._for_xml_id('lims_sale.lims_action_quotation_form')
        action.update({
            'res_id':  order_id.id,
            'view_id': form.id,
        })
        return action

    def _prepare_sale_order(self, section_model):
        line_vals = {}
        if section_model == 'lims_parameter_pack':
            line_vals = self.sample_ids._get_invoiceable_parameters()
        elif section_model == 'lims_analysis_request_sample':
            if not all([sample_id.name for sample_id in self.sample_ids]):
                raise exceptions.MissingError(_("To group by sample you have to give each one of them a name"))

            self._rename_sample_duplicate()

            for sample_id in self.sample_ids:
                parameter_vals = sample_id._get_invoiceable_parameters()
                product_vals = {}

                if parameter_vals:
                    for parameter_name, product_infos in parameter_vals.items():
                        for product, info in product_infos.items():
                            if product in product_vals:
                                product_vals[product]['quantity'] += info['quantity']
                                product_vals[product]['parameter_ids'] += info['parameter_ids']
                            else:
                                product_vals[product] = info
                    if not line_vals.get(sample_id.name):
                        line_vals.update({
                            sample_id.name: product_vals
                        })
                    else:
                        line_vals[sample_id.name].update(product_vals)
        return line_vals

    def _rename_sample_duplicate(self, names=None):
        """
        Avoid to erase previous data with the same sample name, when generate an SO by sample_name from request.
        :param names:
        :return:
        """
        if not names:
            names = {}
        for sample_id in self.sample_ids:
            if sample_id.name in names:
                names[sample_id.name] += 1
                sample_id.name = "{} ({})".format(sample_id.name, names[sample_id.name])
            else:
                names[sample_id.name] = 1

    def do_confirmed(self):
        res = super(LimsAnalysisRequest, self).do_confirmed()
        for record in self.filtered(lambda r: r.order_id and r.order_id.sudo().state in ['draft', 'sent']):
            record.order_id.sudo().action_confirm()
        return res

    def check_opened_invoice(self):
        if self.order_id and self.order_id.invoice_count > 0 \
                and self.order_id.invoice_ids.filtered(lambda i: i.state == 'open'):
            raise exceptions.ValidationError(_('You can\'t create a new quotation because '
                                               'there is at least one invoice opened.'))

    def write(self, vals):
        res = super(LimsAnalysisRequest, self).write(vals)
        if (vals.get('product_ids') or vals.get('sample_ids') or vals.get('pricelist_id') or
            vals.get('invoice_to_id')) and self.order_id:
            self.display_warning = True
        return res

    def action_create_sale_order_request(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.create.order.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_request_ids': self.ids}
        }

    def get_line_section_name(self, value):
        return value

    def get_request_line_section_name(self, request_id):
        return request_id.name + (
            (' // ' + ', '.join(request_id.mapped('analysis_ids').mapped('name'))) if request_id.mapped(
                'analysis_ids') else ''
        )
    def get_values_for_create_sample(self, product_id, packs, regulation):
        res = super().get_values_for_create_sample(product_id, packs, regulation)
        res.update({
            'pack_of_pack_invoiced_ids': [(4, pack_id.id) for pack_id in
                                            product_id.get_pack_of_pack_invoiced_ids(regulation)],
            'pack_invoiced_ids': [(4, pack_id.id) for pack_id in product_id.get_pack_invoiced_ids(regulation)],
        })
        return res

    def _prepare_update_request_sample_line(self, sample_id, product_id, update_elements=None):
        res = super()._prepare_update_request_sample_line(sample_id, product_id, update_elements)
        if product_id.pack_invoiced_ids or sample_id.pack_invoiced_ids or sample_id.pack_of_pack_invoiced_ids:
            regulation_ids = self.env['lims.regulation'].browse(sample_id.get_regulation())
            res['pack_invoiced_ids'] = product_id.get_pack_invoiced_ids(regulation_ids)
            res['pack_of_pack_invoiced_ids'] = product_id.get_pack_of_pack_invoiced_ids(regulation_ids)
        return res

    def create_sale_order_request(self):
        analysis_request_ids = self
        if self.env.context.get('analysis_request_ids'):
            analysis_request_ids = self.browse(self.env.context.get('analysis_request_ids').ids)
        if analysis_request_ids.filtered(lambda r: not r.invoice_to_id):
            raise exceptions.ValidationError(_('Some requests have no clients.'))
        if analysis_request_ids.filtered(lambda r: not r.pricelist_id):
            raise exceptions.ValidationError(_('There is no pricelist set in at least one request'))
        if analysis_request_ids.mapped('labo_id').mapped('company_id') != self.env.user.company_id:
            raise exceptions.ValidationError(_('You can not create a quotation for different company'))
        analysis_request_ids.get_all_sale_orders().with_context(disable_cancel_warning=True).action_cancel()
        if analysis_request_ids.mapped('analysis_ids').filtered(lambda a: a.sale_order_id):
            analysis_request_ids.mapped('analysis_ids').mapped('sale_order_id').action_cancel()

        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        for partner_id in set(analysis_request_ids.mapped('invoice_to_id')):
            request_ids = analysis_request_ids.filtered(lambda r: r.invoice_to_id == partner_id)

            pricelist_ids = request_ids.mapped('pricelist_id')
            for pricelist_id in pricelist_ids:
                request_ids_group_by_pricelist = request_ids.filtered(lambda r: r.pricelist_id == pricelist_id)

                order_vals = {
                    'partner_id': partner_id.id,
                    'client_order_ref': ', '.join(request_ids_group_by_pricelist.filtered('customer_order_ref').mapped('customer_order_ref')),
                    'customer_ref': ', '.join(request_ids_group_by_pricelist.filtered('customer_ref').mapped('customer_ref')),
                    'partner_contact_ids': [
                        (4, partner_contact_id.id) for partner_contact_id in request_ids_group_by_pricelist.mapped('partner_contact_ids')
                    ],
                    'pricelist_id': pricelist_id.id,
                    'payment_term_id': partner_id.property_payment_term_id.id,
                    'analysis_request_ids': [Command.set(request_ids_group_by_pricelist.ids)],
                    'analysis_ids': [Command.set(request_ids_group_by_pricelist.analysis_ids.ids)],
                    'company_id': self.env.user.company_id.id
                }
                if self.env.context.get('order_template'):
                    order_vals.update({
                        'sale_order_template_id': self.env.context.get('order_template')
                    })
                ctx_vals = self.env.context.get('order_vals')
                if ctx_vals and type(ctx_vals) == dict:
                    order_vals.update(
                        self.env.context.get('order_vals')
                    )
                order_id = self.env['sale.order'].with_context(bypass_check_locked_analysis=True).create(order_vals)
                order_id._onchange_sale_order_template_id()
                sale_order_obj += order_id
                for request_id in request_ids_group_by_pricelist:
                    request_id.order_id = order_id

                    sale_order_line_obj.create({
                        'order_id': order_id.id,
                        'name': self.get_request_line_section_name(request_id),
                        'request_id': request_id.id,
                        'display_type': 'line_section',
                    })

                    line_vals = request_id.sample_ids._get_invoiceable_parameters()
                    for line_val in line_vals:
                        for product_id in line_vals[line_val]:
                            product_vals = line_vals[line_val][product_id]
                            sale_order_line_id = sale_order_line_obj.create({
                                'product_id': product_id.id,
                                'product_uom': product_id.uom_id.id,
                                'product_uom_qty': product_vals.get('quantity'),
                                'parameter_ids': product_vals.get('parameter_ids'),
                                'sample_id': product_vals.get('sample_id'),
                                'order_id': order_id.id,
                                'request_id': request_id.id,
                            })
        return {
            'name': _('Sale orders from requests'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_obj.ids)],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'group_by': 'partner_id'}
        }

    def open_invoices(self):
        order_ids = self.get_all_sale_orders()
        invoice_ids = order_ids.invoice_ids
        form_id = self.env.ref('account.view_move_form')
        tree_id = self.env.ref('account.view_move_tree')
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree, form',
            'view_type': 'form',
            'target': 'current',
            'views': [
                (tree_id.id, 'tree'),
                (form_id.id, 'form'),
            ],
            'domain': [('id', 'in', invoice_ids.ids)],
            'context': {'default_analysis_request_id': self.id,
                        'default_move_type': 'out_invoice',
                        'default_partner_id': self.invoice_to_id.id or self.partner_id.id}
        }

    def open_sale_orders(self):
        self.ensure_one()
        form_id = self.env.ref('sale.view_order_form')
        tree_id = self.env.ref('sale.view_quotation_tree')

        return {
            'name': _('Sale orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree, form',
            'target': 'current',
            'views': [
                (tree_id.id, 'tree'),
                (form_id.id, 'form'),
            ],
            'domain': ['|', ('analysis_request_id', '=', self.id), ('analysis_request_ids', 'in', [self.id])]
        }

    def get_all_sale_orders(self):
        return self.env['sale.order'].search([
            '|', ('analysis_request_id', 'in', self.ids), ('analysis_request_ids', 'in', self.ids)
        ])

    def get_portal_order_id(self):
        self.ensure_one()
        order_id = False
        try:
            order_id = self.order_id
        finally:
            return order_id
