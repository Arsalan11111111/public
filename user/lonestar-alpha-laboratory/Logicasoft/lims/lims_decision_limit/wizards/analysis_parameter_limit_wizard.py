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
from odoo import models, fields, _, api
import json


def get_data_dictonnary():
    """
    Used to build base structure for parameter limit report
    :return:
    """

    return {'Parameters': [],
            'Values': [],
            'Units': [],
            'States': [],
            'Report limit values': [],
            }


def get_data_dictonnary_structure(collections, custom_set=False):
    """
    Used to build base structure for parameter limit report
    Extend with collections and/or custom set

    :param collections:
    :param custom_set:
    :return:
    """
    structure = get_data_dictonnary()
    if collections:
        structure['Collections'] = {c.name: {'States': [], 'Report limit values': []} for c in collections}
    if custom_set and collections:
        structure['Collections'].update({' ': {'States': [], 'Report limit values': []}})
    if custom_set and not collections:
        structure['Collections'] = {' ': {'States': [], 'Report limit values': []}}
    return structure


def get_result_state():
    """
    Used to filter result in state.
    :return:
    """
    return ['validated']


def get_state(result, customs_limits, lang):
    """
    Evaluate result value with a custom_set of limit for result type NU,CA only
    :param result:
    :param customs_limits:
    :param lang:
    :return:
    """
    result_format = result.method_param_charac_id.format
    if result_format in ['ca', 'nu']:
        return result.get_result_limit(result.get_result_value(options='raw'),
                                       custom_limits=customs_limits).with_context(lang=lang).state
    return result.with_context(lang=lang).state


class AnalysisParameterLimitWizard(models.TransientModel):
    _name = 'analysis.parameter.limit.wizard'
    _description = 'Wizard for applying parameter limits to an analysis'

    analysis_id = fields.Many2one('lims.analysis')
    limit_set_ids = fields.Many2many('lims.parameter.limit.set')
    collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                      relation='analysis_parameter_limit_wizard_collection_rel')
    conform_collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                              relation='analysis_parameter_limit_wizard_conform_collection_rel')
    non_conform_collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                                  relation='analysis_parameter_limit_wizard_non_conform_collection_rel')

    filtered_collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                               relation='analysis_parameter_limit_wizard_filtered_collection_rel')

    filtered_set_ids = fields.Many2many('lims.parameter.limit.set',
                                        relation='analysis_parameter_limit_wizard_filtered_set_rel')
    parameter_ids = fields.Many2many('lims.parameter', compute='compute_parameter_ids')

    is_specific_filter = fields.Boolean('Specific filter', default=False,
                                        help='Limits set must have all filter defined below in their configuration')

    rel_matrix_id = fields.Many2one('lims.matrix', related='analysis_id.matrix_id')
    is_matrix = fields.Boolean('Filter matrix')
    rel_regulation_id = fields.Many2one('lims.regulation', related='analysis_id.regulation_id')
    is_regulation = fields.Boolean('Filter regulation')
    rel_partner_id = fields.Many2one('res.partner', related='analysis_id.partner_id')
    is_partner = fields.Boolean('Filter partner')
    rel_product_id = fields.Many2one('product.product', related='analysis_id.product_id')
    is_product = fields.Boolean('Filter product')

    @api.depends('analysis_id')
    def compute_parameter_ids(self):
        """
        Find parameter in analysis result set, only useful with format result NU, CA
        :return:
        """
        parameter_ids = False
        if self.analysis_id:
            parameter_ids = self.analysis_id.result_num_ids.filtered(
                lambda r: r.rel_type == 'validated').method_param_charac_id
            parameter_ids += self.analysis_id.result_compute_ids.filtered(
                lambda r: r.rel_type == 'validated').method_param_charac_id
            parameter_ids = parameter_ids.parameter_id
        self.parameter_ids = parameter_ids

    def get_domain(self, domain=False):
        """
        Build dynamic domain for self.env[] for limits collections and limits sets
        :param domain:
        :return:
        """
        if not domain:
            domain = []
        domain_base = [False] if self.is_specific_filter else [False, False]
        if self.rel_matrix_id and self.is_matrix:
            domain_base[0] = self.rel_matrix_id.id
            domain.append(('matrix_id', 'in', domain_base.copy()))
        if self.rel_regulation_id and self.is_regulation:
            domain_base[0] = self.rel_regulation_id.id
            domain.append(('regulation_id', 'in', domain_base.copy()))
        if self.rel_partner_id and self.is_partner:
            domain_base[0] = self.rel_partner_id.id
            domain.append(('partner_id', 'in', domain_base.copy()))
        if self.rel_product_id and self.is_product:
            domain_base[0] = self.rel_product_id.id
            domain.append(('product_id', 'in', domain_base.copy()))
        return domain

    @api.onchange('analysis_id', 'is_specific_filter', 'is_matrix', 'is_regulation', 'is_product', 'is_partner')
    def possible_limit_set_ids(self):
        """
        Update filtered field (Collections and Sets) to create dynamic domain in view.
        :return:
        """
        if self.analysis_id and self.parameter_ids:
            self.filtered_set_ids = self.env['lims.parameter.limit.set'].search(
                self.get_domain([('parameter_id', 'in', self.parameter_ids.ids)]))
            self.filtered_collection_ids = self.env['lims.parameter.limit.collection'].search(self.get_domain())

    def apply_limit_sets(self, datas=None):
        """
        Main function for analysis.parameter.limit.wizard, pre calculate all information to send in report
        :param datas:
        :return:
        """
        lang = self.analysis_id.partner_id.lang or self.env.user.lang
        if not datas:
            datas = {}
        datas[self.analysis_id.name] = get_data_dictonnary_structure(self.collection_ids, self.limit_set_ids)
        for result in self.analysis_id.get_results_filtered(stage=get_result_state()):
            self.get_result_data_values(result, datas, lang)
            for collection in self.collection_ids:
                self.get_limit_set_data_values(datas, collection.name, result, collection.set_ids, lang)
            if self.limit_set_ids:
                self.get_limit_set_data_values(datas, ' ', result, self.limit_set_ids, lang)
        self.generate_conclusion_line(datas[self.analysis_id.name])
        return datas

    def get_result_data_values(self, result, datas, lang):
        """
        Update data with basic result information.
        :param result:
        :param datas:
        :param lang:
        :return:
        """
        datas[self.analysis_id.name]['Parameters'].append(
            result.with_context(
                lang=lang).method_param_charac_id.parameter_id.name if result.method_param_charac_id.parameter_id else ' ')
        datas[self.analysis_id.name]['Values'].append(result.with_context(lang=lang).get_result_value() or ' ')
        datas[self.analysis_id.name]['Units'].append(
            result.with_context(lang=lang).get_result_uom().name if result.get_result_uom() else ' ')
        datas[self.analysis_id.name]['States'].append(result.with_context(lang=lang).get_state_translated() or ' ')
        datas[self.analysis_id.name]['Report limit values'].append(result.with_context(lang=lang).report_limit_value or ' ')
        return datas

    def get_limit_set_data_values(self, datas, collection_name, result, sets, lang):
        """
        Used when collection or set must be evaluated.
        Add in end of list 'Collections' , 'States'[] and 'Report limit values'[], the result of evaluation with the set
        :param datas:
        :param collection_name:
        :param result:
        :param sets:
        :param lang:
        :return:
        """
        state = False
        report_limit_value = False
        if result.method_param_charac_id.parameter_id.id in sets.parameter_id.ids:
            filtered_set = sets.filtered(
                lambda s: s.parameter_id.id == result.method_param_charac_id.parameter_id.id)[0]
            if filtered_set.limit_ids:
                state = result.get_state_translated(get_state(result, filtered_set.limit_ids, lang))
                report_limit_value = filtered_set.with_context(lang=lang).report_limit_value
        elif result.method_param_charac_id.format not in ['nu', 'ca']:
            state = result.get_state_translated()
            report_limit_value = result.with_context(lang=lang).report_limit_value
        datas[self.analysis_id.name]['Collections'][collection_name]['States'].append(state or ' ')
        datas[self.analysis_id.name]['Collections'][collection_name]['Report limit values'].append(report_limit_value or ' ')
        return datas

    def generate_conclusion_line(self, datas):
        """
        Add in the end of all lists 'State'[], 'Report limit values'[] the overall conclusion of current list 'State'
        1 Rule if anything is not conform -> conclusion is not conform
        2 Rule if anything is conform -> conclusion is conform
        3 Rule By default -> conclusion is False
        :param datas:
        :return:
        """
        if datas['States']:
            datas['Parameters'].append(_('State :'))
            datas['Values'].append(' ')
            datas['Units'].append(' ')
            datas['Report limit values'].append(' ')
            datas['States'].append(self.analysis_id.get_state_translated() or ' ')
            conform_collections = self.env['lims.parameter.limit.collection']
            non_conform_collections = self.env['lims.parameter.limit.collection']
            if datas.get('Collections'):
                not_conform = self.env['lims.analysis.result'].get_state_translated('not_conform')
                conform = self.env['lims.analysis.result'].get_state_translated('conform')

                for collection in datas['Collections']:
                    collection_id = self.collection_ids.filtered(lambda c: c.name == collection)
                    collection_id = collection_id[0] if collection_id else collection_id
                    collection_state = ' '
                    if any(s == not_conform for s in datas['Collections'][collection]['States']):
                        collection_state = not_conform
                        non_conform_collections += collection_id
                    elif any(s == conform for s in datas['Collections'][collection]['States']):
                        collection_state = conform
                        conform_collections += collection_id
                    datas['Collections'][collection]['States'].append(collection_state)
                    datas['Collections'][collection]['Report limit values'].append(' ')
            self.conform_collection_ids = conform_collections
            self.non_conform_collection_ids = non_conform_collections
        return datas

    def generate_decision_limit(self):
        self.ensure_one()
        datas = {'result': self.apply_limit_sets()}
        self.env['lims.decision.limit'].create({
            'analysis_id': self.analysis_id.id,
            'collection_ids': self.collection_ids,
            'conform_collection_ids': self.conform_collection_ids,
            'non_conform_collection_ids': self.non_conform_collection_ids,
            'set_ids': self.limit_set_ids,
            'datas': json.dumps(datas)
        })
        return {
            'name': _('Decision limit : {}').format(self.analysis_id.name if self.analysis_id else "N/A"),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.decision.limit',
            'view_mode': 'tree,form',
            'domain': [('analysis_id', '=', self.analysis_id.id if self.analysis_id else False)]
        }

