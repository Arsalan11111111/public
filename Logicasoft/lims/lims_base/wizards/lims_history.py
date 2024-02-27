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
from odoo import fields, models, api,  _
from statistics import mean


class LimsHistory(models.TransientModel):
    _name = 'lims.history'
    _description = 'Lims History'

    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', string='Parameter')
    nb_history = fields.Integer(string='NB History')
    date_type = fields.Selection(
        [('rel_date_sample', _('Date Sample')), ('date_start', _('Date Start')), ('date_result', _('Date Result'))],
        'Date', index=True, default='rel_date_sample')

    result_nu_ids = fields.Many2many('lims.analysis.numeric.result')
    nb_result_nu_ids = fields.Integer()
    result_compute_ids = fields.Many2many('lims.analysis.compute.result')
    nb_result_compute_ids = fields.Integer()
    result_sel_ids = fields.Many2many('lims.analysis.sel.result')
    nb_result_sel_ids = fields.Integer()
    result_txt_ids = fields.Many2many('lims.analysis.text.result')
    nb_result_txt_ids = fields.Integer()

    n_results = fields.Float(string='Count', compute='compute_statistics')
    mean_results = fields.Float(string='Mean', compute='compute_statistics', digits='Analysis Result')
    min_results = fields.Float(string='Min', compute='compute_statistics', digits='Analysis Result')
    max_results = fields.Float(string='Max', compute='compute_statistics', digits='Analysis Result')

    product_id = fields.Many2one('product.product', string='Product')
    is_product = fields.Boolean('Filter product', default=1)
    partner_id = fields.Many2one('res.partner', string='Customer')
    is_partner = fields.Boolean('Filter customer', default=1)
    batch_id = fields.Many2one('lims.batch', string='Batch')
    is_batch = fields.Boolean('Filter batch', default=0)
    user_id = fields.Many2one('res.users', string='Operator Input')
    is_user = fields.Boolean('Filter operator', default=0)

    @api.depends('nb_result_nu_ids', 'result_nu_ids.corrected_value', 'result_compute_ids', 'result_compute_ids.value')
    def compute_statistics(self):
        for record in self:
            values = [0]
            if record.nb_result_nu_ids and record.result_nu_ids:
                values = record.result_nu_ids.mapped('corrected_value')
            elif record.nb_result_compute_ids and record.result_compute_ids:
                values = record.result_compute_ids.mapped('value')
            record.n_results = len(values)
            record.mean_results = mean(values)
            record.min_results = min(values)
            record.max_results = max(values)

    @api.onchange('method_param_charac_id', 'date_type', 'nb_history', 'is_product', 'is_partner', 'is_batch', 'is_user')
    def get_result(self):
        para_format = self.method_param_charac_id.parameter_id.format
        domain = self.get_domain()
        if not self.nb_history and self.method_param_charac_id.nb_history:
            self.nb_history = self.method_param_charac_id.nb_history
        nb_history = self.nb_history if abs(self.nb_history) < 100 else 100
        date_type = self.date_type if self.date_type else 'rel_date_sample'

        if nb_history and para_format:
            if para_format == 'nu':
                self.result_nu_ids = self.env['lims.analysis.numeric.result'].search(domain,
                                                                                     order=date_type + str(' desc'),
                                                                                     limit=nb_history)
                self.nb_result_nu_ids = len(self.result_nu_ids)
            elif para_format == 'ca':
                self.result_compute_ids = self.env['lims.analysis.compute.result'].search(domain, order=date_type + str(
                    ' desc'), limit=nb_history)
                self.nb_result_compute_ids = len(self.result_compute_ids)
            elif para_format == 'se':
                self.result_sel_ids = self.env['lims.analysis.sel.result'].search(domain,
                                                                                  order=date_type + str(' desc'),
                                                                                  limit=nb_history)
                self.nb_result_sel_ids = len(self.result_sel_ids)
            elif para_format == 'tx':
                self.result_txt_ids = self.env['lims.analysis.text.result'].search(domain,
                                                                                   order=date_type + str(' desc'),
                                                                                   limit=nb_history)
                self.nb_result_txt_ids = len(self.result_txt_ids)

    def get_domain(self):
        stage_done = self.env['lims.result.stage'].search([('type', '=', 'validated')], limit=1)
        domain = [('method_param_charac_id', '=', self.method_param_charac_id.id),
                  ('stage_id', '=', stage_done.id),
                  (self.date_type if self.date_type else 'rel_date_sample', '!=', False)
                  ]
        if self.partner_id and self.is_partner:
            domain.append(('rel_partner_id', '=', self.partner_id.id))
        if self.product_id and self.is_product:
            domain.append(('analysis_id.product_id', '=', self.product_id.id))
        if self.batch_id and self.is_batch:
            domain.append(('rel_batch_id', '=', self.batch_id.id))
        if self.user_id and self.is_user:
            domain.append(('user_id', '=', self.user_id.id))

        return domain

    # When u display graph, if rel_date_sample has same value than an another one, the values are added..
    # for dodge this problem, I create an unique value with the date
    def compute_display_name_for_history(self, results):
        i = 1
        for result in results:
            if result.rel_date_sample:
                date_str = fields.Datetime.to_string(result.rel_date_sample)
            elif result.date_result:
                date_str = fields.Datetime.to_string(result.date_result)
            else:
                date_str = '-'
            result.display_name_for_history = str(i).zfill(2) + ' : ' + date_str
            i += 1

    def open_graph(self):
        view = False
        graph_mode = 'line'
        if self.result_nu_ids:
            model = 'lims.analysis.numeric.result'
            view = self.env.ref('lims_base.lims_analysis_result_graph_history')
            self.compute_display_name_for_history(self.result_nu_ids)
            ids = self.result_nu_ids.sorted(lambda r: r.display_name_for_history).ids
        elif self.result_compute_ids:
            model = 'lims.analysis.compute.result'
            view = self.env.ref('lims_base.lims_analysis_compute_result_graph_history')
            self.compute_display_name_for_history(
                self.result_compute_ids.filtered(lambda r: not r.display_name_for_history))
            ids = self.result_compute_ids.sorted(lambda r: r.display_name_for_history).ids
        elif self.result_sel_ids:
            graph_mode = 'pie'
            model = 'lims.analysis.sel.result'
            view = self.env.ref('lims_base.lims_analysis_sel_result_graph_history')
            ids = self.result_sel_ids.ids
        elif self.result_txt_ids:
            graph_mode = 'pie'
            model = 'lims.analysis.text.result'
            view = self.env.ref('lims_base.lims_analysis_text_result_graph_history')
            ids = self.result_txt_ids.ids
        if view:
            return {
                'name': _('History'),
                'type': 'ir.actions.act_window',
                'context': {'graph_mode': graph_mode, 'create': False, 'edit': False},
                'view_mode': 'graph',
                'view_id': view.id,
                'res_model': model,
                'domain': [('id', 'in', ids)],
                'target': 'current',
            }
