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
from odoo import fields, models, api


class DuplicateTourWizard(models.TransientModel):
    _name = 'duplicate.tour.wizard'
    _description = 'Duplicate Tour Wizard'

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    date = fields.Datetime('Date', help="Defines the date of the new tour, and the planned dates of its samples")
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', default=get_default_laboratory)
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler')
    sampler_team_id = fields.Many2one('lims.sampler.team', 'Sampler Team')
    rel_sampler_ids = fields.Many2many('hr.employee.public', related='sampler_team_id.sampler_ids',
                                       string="Team's sampler")
    tour_ids = fields.Many2many('lims.tour', string='Tour')

    def do_duplicate_tour(self):
        self.ensure_one()
        tour_obj = self.env['lims.tour']
        vals_default = {
            'laboratory_id': self.laboratory_id.id,
            'sampler_id': self.sampler_id.id if self.sampler_id else False,
            'sampler_team_id': self.sampler_team_id.id if self.sampler_team_id else False,
            'state': 'plan',
            'name': '/',
            'date': self.date
        }
        method_param_charac_ids = self.tour_ids.tour_line_ids.method_param_charac_ids
        pack_ids = self.tour_ids.tour_line_ids.pack_ids
        tab_result = self.fill_tab(method_param_charac_ids, pack_ids)
        vals_num = []
        vals_se = []
        vals_ca = []
        vals_tx = []
        plan_stage_id = self.env['lims.result.stage'].search([('type', '=', 'plan')], limit=1)
        for tour in self.tour_ids:
            vals = vals_default.copy()
            vals.update({
                'note': tour.note,
                'tour_name_id': tour.tour_name_id.id,
            })
            new_tour = tour_obj.create(vals)
            new_tour_line_ids = self.env['lims.tour.line']
            for tour_line in tour.tour_line_ids:
                vals = tour_line.analysis_id.get_vals_for_recurrence()
                vals.update({
                    'sampler_id': self.sampler_id.id,
                    'laboratory_id': self.laboratory_id.id,
                    'date_plan': self.date,
                })
                new_analysis = tour_line.analysis_id.create(vals)
                vals = {
                    'sequence': tour_line.sequence,
                    'tour_id': new_tour.id,
                    'analysis_id': new_analysis.id,
                }
                new_tour_line_ids += tour.tour_line_ids.create(vals)
                new_analysis.update({
                    'tour_id': new_tour.id,
                    'date_plan': self.date,
                })
                for method_param_charac_id in tour_line.method_param_charac_ids:
                    self.create_result(new_analysis, method_param_charac_id, tab_result, plan_stage_id, vals_num,
                                       vals_se, vals_ca, vals_tx)
                pack_of_pack_ids = tour_line.pack_ids.filtered(lambda p: p.is_pack_of_pack)
                pack_ids = pack_of_pack_ids.pack_of_pack_ids.pack_id
                pack_ids += tour_line.pack_ids.filtered(lambda p: not p.is_pack_of_pack and p not in pack_ids)
                for pack in pack_ids:
                    for method_param_charac_id in pack.parameter_ids.method_param_charac_id:
                        self.create_result(new_analysis, method_param_charac_id, tab_result, plan_stage_id, vals_num,
                                           vals_se, vals_ca, vals_tx)
            new_tour.tour_line_ids = new_tour_line_ids
            tour_obj += new_tour

        result_nu_obj = self.env['lims.analysis.numeric.result']
        result_sel_obj = self.env['lims.analysis.sel.result']
        result_ca_obj = self.env['lims.analysis.compute.result']
        result_tx_obj = self.env['lims.analysis.text.result']
        for val in vals_num:
            result = result_nu_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            result.update({
                'limit_result_ids': [(0, 0, {
                    'operator_from': limit.operator_from,
                    'limit_value_from': limit.limit_value_from,
                    'operator_to': limit.operator_to,
                    'limit_value_to': limit.limit_value_to,
                    'type_alert': limit.type_alert,
                    'state': limit.state,
                    'message': limit.message
                }) for limit in tab_result[val.get('method_param_charac_id')].limit_result_ids]
            })
        for val in vals_se:
            result_sel_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
        for val in vals_ca:
            result = result_ca_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            result.update({
                'correspondence_ids': [(0, 0, {
                    'method_param_charac_id': correspondence_id.method_param_charac_id.id,
                    'correspondence': correspondence_id.correspondence,
                    'use_function': correspondence_id.use_function,
                    'is_optional': correspondence_id.is_optional,
                }) for correspondence_id in tab_result[val.get('method_param_charac_id')].correspondence_ids],
                'limit_compute_result_ids': [(0, 0, {
                    'operator_from': limit.operator_from,
                    'limit_value_from': limit.limit_value_from,
                    'operator_to': limit.operator_to,
                    'limit_value_to': limit.limit_value_to,
                    'type_alert': limit.type_alert,
                    'state': limit.state,
                    'message': limit.message
                }) for limit in tab_result[val.get('method_param_charac_id')].limit_compute_result_ids]
            })
        for val in vals_tx:
            result_tx_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
        tour_obj.tour_line_ids.analysis_id.create_sop()
        view = {'name': 'Tour',
                'view_mode': 'form,tree,calendar,pivot,graph',
                'res_model': 'lims.tour',
                'type': 'ir.actions.act_window',
                'target': 'current',
                }
        if len(tour_obj) != 1:
            view['domain'] = [('id', 'in', tour_obj.ids)]
            view['view_mode'] = 'tree,form,calendar,pivot,graph'
        else:
            view['res_id'] = tour_obj.id
        return view

    def fill_tab(self, method_param_charac_ids, pack_ids):
        tab_result = {}
        result_nu_obj = self.env['lims.analysis.numeric.result'].sudo()
        result_sel_obj = self.env['lims.analysis.sel.result'].sudo()
        result_ca_obj = self.env['lims.analysis.compute.result'].sudo()
        result_tx_obj = self.env['lims.analysis.text.result'].sudo()
        for pack_id in pack_ids.parameter_ids.filtered(lambda p: p.method_param_charac_id):
            method_param_id = pack_id.method_param_charac_id
            result_vals = {
                'pack_id': pack_id.pack_id.id,
                'method_param_charac_id': method_param_id.id,
            }
            format = method_param_id.format
            if not tab_result.get(method_param_id.id):
                if format == 'nu':
                    tab_result[method_param_id.id] = result_nu_obj.create(result_vals)
                elif format == 'se':
                    tab_result[method_param_id.id] = result_sel_obj.create(result_vals)
                elif format == 'ca':
                    tab_result[method_param_id.id] = result_ca_obj.create(result_vals)
                elif format == 'tx':
                    tab_result[method_param_id.id] = result_tx_obj.create(result_vals)
        for method_param_charac_id in method_param_charac_ids:
            result_vals = {
                'method_param_charac_id': method_param_charac_id.id,
            }
            format = method_param_charac_id.format
            if not tab_result.get(method_param_charac_id.id):
                if format == 'nu':
                    tab_result[method_param_charac_id.id] = result_nu_obj.create(result_vals)
                elif format == 'se':
                    tab_result[method_param_charac_id.id] = result_sel_obj.create(result_vals)
                elif format == 'ca':
                    tab_result[method_param_charac_id.id] = result_ca_obj.create(result_vals)
                elif format == 'tx':
                    tab_result[method_param_charac_id.id] = result_tx_obj.create(result_vals)
        return tab_result

    def create_result(self, analysis_id, method_param_id, tab_result, plan_stage_id, vals_num, vals_se, vals_ca, vals_tx):
        """
        create (copy) result from the tab_result with necessary information
        :param analysis_id:
        :param method_param_id:
        :param tab_result:
        :param default:
        :param plan_stage_id:
        :return:
        """
        default = {'analysis_id': analysis_id.id}
        sop_id = analysis_id.mapped('sop_ids').filtered(
            lambda s: s.method_id == method_param_id.method_id and s.rel_type != 'cancel')
        if sop_id:
            default.update({'sop_id': sop_id.id})
        if not sop_id or sop_id.rel_type == 'draft':
            default.update({'stage_id': plan_stage_id.id})
        format = method_param_id.format
        vals = tab_result[method_param_id.id].copy_data(default=default)[0]
        if format == 'nu':
            if not any(vals.get('method_param_charac_id') == val_num.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_num.get('analysis_id') for val_num in vals_num):
                vals_num.append(vals)
        elif format == 'se':
            if not any(vals.get('method_param_charac_id') == val_se.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_se.get('analysis_id') for val_se in vals_se):
                vals_se.append(vals)
        elif format == 'ca':
            if not any(vals.get('method_param_charac_id') == val_ca.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_ca.get('analysis_id') for val_ca in vals_ca):
                vals_ca.append(vals)
        elif format == 'tx':
            if not any(vals.get('method_param_charac_id') == val_tx.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_tx.get('analysis_id') for val_tx in vals_tx):
                vals_tx.append(vals)
