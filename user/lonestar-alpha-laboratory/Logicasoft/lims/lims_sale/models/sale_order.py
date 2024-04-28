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
from odoo import models, fields, api, exceptions, Command, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analysis_request_id = fields.Many2one('lims.analysis.request', 'Request',
                                          help="This is the most recent request builded from this sale order. "
                                               "If you confirm the sale order, it will confirm this request.")
    partner_contact_ids = fields.Many2many('res.partner', string='Customer contacts')
    signatory_id = fields.Many2one('res.users', 'Signatory')
    analysis_ids = fields.One2many('lims.analysis', 'sale_order_id', string='Analysis', groups="lims_base.viewer_group")
    nb_analysis = fields.Integer(compute='compute_nb_analysis', string='NB Analysis', groups="lims_base.viewer_group")
    customer_ref = fields.Char('Customer Ref')
    print_parameters = fields.Boolean(string="Print Parameter on PDF ?",
                                      help="If this is checked, this will add on the sale order's pdf a table "
                                           "under each sale order lines that summarize information about parameter "
                                           "involved in that line,  such as his method, his standard, his loq, etc...")
    analysis_request_ids = fields.Many2many('lims.analysis.request', 'rel_request_sale_order', 'request', 'sale_order',
                                            string='Requests',
                                            help="This is all the requests that has been builded from this sale order.")
    accreditation_ids = fields.Many2many('lims.accreditation', string='Accreditations',
                                         help="It add before the note of the sale order's pdf a list of accreditations "
                                              "with their logos and their names.")
    request_count = fields.Integer(compute='compute_request_count', string='Request(s)',
                                   groups="lims_base.viewer_group")

    def compute_request_count(self):
        for record in self:
            record.request_count = len(record.analysis_request_ids)

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.analysis_ids)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.analysis_request_id.state == 'draft':
            self.analysis_request_id.do_confirmed()
        return res

    def open_analysis(self):
        self.ensure_one()
        return {
            'name': 'Analysis',
            'view_mode': 'tree,form',
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', self.analysis_ids.ids)],
        }

    def copy(self, default=None):
        if self.analysis_request_id or self.analysis_ids:
            raise exceptions.ValidationError(_('You can not duplicate if at least one '
                                               'line is linked to an analysis request or an analysis'))
        return super(SaleOrder, self).copy(default)

    def create_analysis_request_wizard(self):
        self.ensure_one()

        if self.analysis_request_ids:
            return {
                'name': _('Create analysis request'),
                'view_mode': 'form',
                'res_model': 'create.analysis.request.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_order_id': self.id}
            }
        self.create_analysis_request()

    def create_analysis_request(self):
        self.ensure_one()

        laboratory = self.env.user.default_laboratory_id or (
            self.env['lims.laboratory'].search([('default_laboratory', '=', True)], limit=1)
        )
        request_id = self.env['lims.analysis.request'].create({
            'order_id': self.id,
            'labo_id': laboratory.id,
            'partner_id': self.partner_id.id,
            'invoice_to_id': self.partner_id.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id
        })

        notes = []
        values = []
        all_packs = self.env['lims.parameter.pack'].search([('product_id', 'in', self.order_line.product_id.ids)])
        for line in self.order_line:
            if line.display_type == 'line_note':
                notes.append(line.name)

            product = line.product_id
            packs = all_packs.filtered(lambda p: (p.product_id == product) and p.state == 'validated')
            if packs:
                values.append({
                    'request_id': request_id.id,
                    'matrix_id': packs[0].matrix_id.id,
                    'pack_ids': [Command.set([packs[0].id])],
                    'qty': line.product_uom_qty
                })
        self.env['lims.request.product.pack'].create(values)

        request_id.update({
            'comment': '<br/>'.join(notes)
        })

        self.update({
            'analysis_request_id': request_id.id,
            'analysis_request_ids': [Command.link(request_id.id)]
        })

        return {
            'name': _('Analysis request'),
            'view_mode': 'tree,form',
            'res_model': 'lims.analysis.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', '=', request_id.id)],
        }

    def open_requests(self):
        self.ensure_one()
        form_id = self.env.ref('lims_base.lims_analysis_request_form')
        tree_id = self.env.ref('lims_base.lims_analysis_request_tree')

        return {
            'name': _('Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.request',
            'view_mode': 'tree, form',
            'target': 'current',
            'views': [
                (tree_id.id, 'tree'),
                (form_id.id, 'form'),
            ],
            'domain': [('id', 'in', self.analysis_request_ids.ids)]
        }

    def get_request_and_analysis_packs_and_pack_of_packs(self):
        pack_object = self.env['lims.parameter.pack']
        analysis_object = self.env['lims.analysis']
        packs = pack_object

        for record in self:
            analysis_linked_samples = ((record.analysis_request_ids and
                                        record.analysis_request_ids.sample_ids.analysis_id) or analysis_object)
            packs += record.analysis_request_ids.get_request_packs_and_pack_of_packs()
            packs += ((record.analysis_ids and record.analysis_ids.filtered(
                lambda a: a._origin.id not in analysis_linked_samples.ids).get_analysis_packs_and_pack_of_packs())
                      or pack_object)
        return packs

    def get_highest_working_day(self):
        self.ensure_one()
        pack_object = self.env['lims.parameter.pack']
        pack_ids = self.get_request_and_analysis_packs_and_pack_of_packs()
        pack_ids = pack_object.get_distinct_packs(pack_ids)
        return (pack_ids and max(pack_ids.mapped('working_day'))) or False
