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
from odoo import models, fields, api, exceptions, _, Command
from odoo.tools.safe_eval import safe_eval
from odoo.tools.float_utils import float_compare, float_round
import math
import re
from statistics import mean, median, stdev, variance


def compute_log(vals):
    """
    Other compute functions take a single parameter (in a list). This one takes 2, but what's sent when expression
    is evaluated is a tuple. So we've got to do an intermediary function to change this tuple into 2 parameters
    :param vals: tuple with value + base
    :return: result
    """
    return math.log(vals[0], vals[1])


COMPUTE_FUNCTIONS = {
    '(mean\((\[[0-9\.\, ]+\])\))': mean,
    '(median\((\[[0-9\.\, ]+\])\))': median,
    '(stdev\((\[[0-9\.\, ]+\])\))': stdev,
    '(min\((\[[0-9\.\, ]+\])\))': min,
    '(max\((\[[0-9\.\, ]+\])\))': max,
    '(sum\((\[[0-9\.\, ]+\])\))': sum,
    '(variance\((\[[0-9\.\, ]+\])\))': variance,
    '(log\(([0-9.]+\,[ 0-9]+)\))': compute_log,
}


class LimsAnalysisComputeResult(models.Model):
    _name = 'lims.analysis.compute.result'
    _description = 'Analysis Compute Result'
    _inherit = ['lims.analysis.result']

    rel_sample_name = fields.Char('Sample Name', related='analysis_id.sample_name', store=True, compute_sudo=True,
                                  help="The sample name of the analysis.")
    formula = fields.Char(help="This formula will be used for the computed result.")
    correspondence_ids = fields.One2many('lims.result.compute.correspondence', 'compute_result_id', readonly=True,
                                         help="List of the variables used in the formula and linked with parameters.")
    value = fields.Float('Value', digits='Analysis Result', copy=False, help="The result of the computed formula.")
    lod = fields.Float('LOD', digits='Analysis Result')
    loq = fields.Float('LOQ', digits='Analysis Result')
    mloq = fields.Float('mLOQ', digits='Analysis Result')
    limit_compute_result_ids = fields.One2many('lims.analysis.limit.compute.result', 'compute_result_id')
    rel_change_loq = fields.Boolean(related='analysis_id.laboratory_id.change_loq', readonly=True, compute_sudo=True)
    is_alert = fields.Boolean(copy=False, help="This is checked if the result get a decision on his conformity "
                                               "that lead to an alert.")
    decision_limit_result_id = fields.Many2one('lims.analysis.limit.compute.result', copy=False,
                                               help="The chosen limit that is finally taken for the conformity.")
    u = fields.Float('U', digits='Analysis Result')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(LimsAnalysisComputeResult, self).create(vals_list)
        if not self.env.context.get('no_limit'):
            res.sudo().create_limit_result()
        return res

    def create_limit_result(self):
        """
        Create the limits for the compute result
        :return:
        """
        for record in self:
            limit_ids = record.sudo().get_limit_result_ids()
            record.create_limit(limit_ids)
            if not limit_ids.filtered(lambda l: l.type_alert == 'limit') and \
                    record.method_param_charac_id.limit_ids and \
                    record.method_param_charac_id.limit_ids.filtered(lambda l: l.type_alert == 'limit'):
                record.create_limit(record.method_param_charac_id.limit_ids.filtered(lambda l: l.type_alert == 'limit'))

    def open_cancel(self):
        return {
            'name': 'Cancel result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.cancel.wizard',
            'context': {'default_result_compute_ids': self.ids},
            'target': 'new',
        }

    def write(self, vals):
        """
        Write the record, Set the user in user_id, check dilution factor, check if result could pass in stage "done",
        Check conformity of the result, Check if result is related to compute result, Check state of the analysis
        :param vals:
        :return:
        """
        for record in self:
            parameter_name = record.method_param_charac_id.display_name if record.method_param_charac_id else ''
            if 'value' in vals:
                digits = self.env['decimal.precision'].precision_get('Analysis Result')
                if not float_compare(float(vals.get('value')), record.value, digits):
                    log = _('Old value: {} | New value: {}').format((round(record.value, digits))
                                                                    if record.state else '-',
                                                                    round(float(vals.get('value'))), digits)
                    result_log = record.prepare_result_log(log)
                    self.env['lims.result.log'].create(result_log)
                if record.value:
                    vals.update({'change': True})
            if 'loq' in vals:
                before_name = record.loq
                after_name = vals['loq']
                change_type = 'LOQ'
                record.record_changes(parameter_name, change_type, before_name, after_name)
            if 'uom_id' in vals:
                before_name = record.uom_id.name if record.uom_id else ''
                after_name = self.env['uom.uom'].browse(vals['uom_id']).name
                change_type = 'UoM'
                record.record_changes(parameter_name, change_type, before_name, after_name)
            if 'comment' in vals and (vals.get('comment') != record.comment):
                before_name = record.comment if record.comment else ''
                after_name = vals['comment']
                change_type = 'Comment'
                record.record_changes(parameter_name, change_type, before_name, after_name)
        if vals.get('value'):
            vals.update({'user_id': self.env.user.id, 'date_result': fields.Datetime.now()})
        if vals.get('result_reason_id'):
            vals.update({'change': True})
        return super(LimsAnalysisComputeResult, self).write(vals)

    def add_parameter_values(self, method_param_charac_id, vals):
        """
        Add some complements form the parameter.

        :param method_param_charac_id:
        :param vals:
        :return:
        """
        vals = super().add_parameter_values(method_param_charac_id, vals)
        vals.update({
            'loq': method_param_charac_id.loq,
            'mloq': method_param_charac_id.mloq,
            'lod': method_param_charac_id.lod,
            'u': method_param_charac_id.u,
            'formula': method_param_charac_id.formula,
            'correspondence_ids': [
                (0, 0, {
                    'method_param_charac_id': correspondence_id.method_param_charac_id.id,
                    'correspondence': correspondence_id.correspondence,
                    'use_function': correspondence_id.rel_use_function,
                    'is_optional': correspondence_id.is_optional,
                }) for correspondence_id in method_param_charac_id.correspondence_ids
            ],
        })
        return vals

    def create_limit(self, limit_ids):
        result_limit_obj = self.env['lims.analysis.limit.compute.result']
        for limit in limit_ids:
            vals = self.get_limit_vals(limit)
            self.limit_compute_result_ids += result_limit_obj.create(vals)

    def get_limit_vals(self, limit):
        self.ensure_one()
        lang = self.analysis_id.partner_id.lang or self.env.user.lang
        vals = {
            'limit_value_from': limit.limit_value_from,
            'limit_value_to': limit.limit_value_to,
            'operator_from': limit.operator_from,
            'operator_to': limit.operator_to,
            'type_alert': limit.type_alert,
            'state': limit.state,
            'message': limit.with_context(lang=lang).message,
            'compute_result_id': self.id,
        }
        return vals

    def get_result_vals(self, correspondence_ids, limits):
        res = super().get_result_vals()
        res.update({
            'correspondence_ids': [(0, 0, {
                'method_param_charac_id': correspondence_id.method_param_charac_id.id,
                'correspondence': correspondence_id.correspondence,
                'use_function': correspondence_id.use_function,
                'is_optional': correspondence_id.is_optional,
            }) for correspondence_id in correspondence_ids],
            'limit_compute_result_ids': [Command.create(limit.get_values()) for limit in limits],
        })
        return res

    def compute_state(self, meth_dict):
        """
        Set the value in the result, Check the result conformity, pass the result in stage "done"
        :return:
        """
        formula = self.formula
        use_loq = self.method_param_charac_id.use_loq
        correspondences = re.findall('\[([A-Za-z0-9éèàçîêù]+)\]*', formula)
        for correspondence in correspondences:
            correspondence_id = self.correspondence_ids.filtered(
                lambda c: c.correspondence == correspondence)
            method_param_charac_id = correspondence_id.method_param_charac_id
            if meth_dict.get(method_param_charac_id) and meth_dict.get(method_param_charac_id).get(
                    'state') in ['validated', 'done']:
                res_value = meth_dict.get(method_param_charac_id).get('value')
                if use_loq:
                    loq = meth_dict.get(method_param_charac_id).get('loq')
                    if res_value < loq:
                        res_value = 0
                formula = formula.replace('[{}]'.format(correspondence), str(res_value))
            elif correspondence_id.is_optional:
                if formula.find('[{}],'.format(correspondence)) >= 0:
                    formula = formula.replace('[{}],'.format(correspondence), '')
                else:
                    formula = formula.replace('[{}]'.format(correspondence), '')
        formula = self.compute_formula(formula)
        try:
            value = safe_eval(formula)
            value = float(value)
        except Exception as e:
            raise exceptions.ValidationError(
                _('An error occurred for parameter {} : make sure that formula returns a number and that '
                  'your formula syntax is correct. ').format(self.method_param_charac_id.name))
        self.update({
            'value': value,
        })
        self.check_result_conformity()
        self.do_done()

    def compute_formula(self, formula):
        if self.method_param_charac_id.use_function:
            for funct in COMPUTE_FUNCTIONS:
                result = re.findall(funct, formula)
                for res in result:
                    formula_to_replace = res[0]
                    formula_to_compute = safe_eval(res[1])
                    formula_res = COMPUTE_FUNCTIONS[funct](formula_to_compute)
                    formula = formula.replace(formula_to_replace, str(formula_res))
        return formula

    def do_cancel(self, cancel_stage_id=False):
        """
        Pass the result in stage "cancel"
        :return:
        """
        super(LimsAnalysisComputeResult, self).do_cancel(cancel_stage_id=cancel_stage_id)
        for record in self:
            log = _('Result is cancelled')
            self.env['lims.result.log'].create({
                'compute_result_id': record.id,
                'user_id': self.env.uid,
                'log': log,
                'date': fields.Datetime.now()
            })
            record.change = True

    def check_result_conformity(self):
        """
        Check if the result is conform, notconform, init or unconclusive
        :return:
        """
        for record in self:
            value = 0 if record.method_param_charac_id.use_loq and record.value < self.loq else record.value
            limit_id = self.get_result_limit(value)
            record.write({'state': limit_id.state if limit_id else 'init',
                          'decision_limit_result_id': limit_id.id if limit_id else False,
                          'is_alert': True if limit_id and limit_id.type_alert == 'alert' else False})

    def get_result_limit(self, value, custom_limits=False):
        """
        Find the limit in all result limits, can be other limits.
        :param value:
        :param custom_limits:
        :return:
        """
        self.ensure_one()
        digits = self.env['decimal.precision'].precision_get('Analysis Result')
        for limit in (custom_limits or self.limit_compute_result_ids):
            operator_from = limit.operator_from
            if operator_from == '=':
                operator_from = '=='
            elif operator_from == '<>':
                operator_from = '!='
            if limit.operator_to:
                operator_to = limit.operator_to
                if operator_to == '=':
                    operator_to = '=='
                elif operator_to == '<>':
                    operator_to = '!='
                formula = '%s %s %s and %s %s %s' % (
                    round(value, digits), operator_from, round(limit.limit_value_from, digits),
                    round(value, digits), operator_to, round(limit.limit_value_to, digits))
            else:
                formula = '%s %s %s' % (
                    round(value, digits), operator_from, round(limit.limit_value_from, digits))
            try:
                if eval(formula):
                    return limit
            except ValueError:
                raise exceptions.ValidationError(_('Parameter is not correctly configured.'))

    def open_wizard_mass_change_result(self):
        """
        Open the wizard mass change result
        :return:
        """
        return {
            'name': 'Mass Change Result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mass.change.result.wizard',
            'context': {'default_analysis_compute_result_ids': self.ids},
            'target': 'new',
        }

    def check_computed_result(self, numeric_result=False, compute_result=False):
        """
        Check for compute the compute_result
        :param numeric_result:
        :param compute_result:
        :return:
        """
        result = numeric_result or compute_result or self
        result_comp_obj = self.env['lims.analysis.compute.result']

        for rec in result:
            numeric_ids = rec.analysis_id.result_num_ids.filtered(lambda r: r.rel_type not in ['cancel', 'rework'])

            # Get all result need to be computed
            computation_ids = rec.analysis_id.result_compute_ids.filtered(
                lambda r: r.rel_type != 'cancel' and r.correspondence_ids.filtered(
                    lambda x: x.method_param_charac_id == rec.method_param_charac_id)) + (
                                      compute_result or result_comp_obj)

            # Get all necessary result for computation (numeric and compute)
            cond_result_needed = lambda y: y.method_param_charac_id.id in computation_ids.correspondence_ids. \
                method_param_charac_id.ids
            num_ids = numeric_ids.filtered(cond_result_needed)
            comp_ids = rec.analysis_id.result_compute_ids.filtered(cond_result_needed)

            check_both = lambda z: z.method_param_charac_id in meth_ids
            for computation_id in computation_ids:
                meth_ids = computation_id.correspondence_ids.filtered(
                    lambda y: not y.is_optional).method_param_charac_id
                num_with_meth = num_ids.filtered(check_both)
                comp_with_meth = comp_ids.filtered(check_both)
                if all(num_id.rel_type in ['validated', 'done'] for num_id in num_with_meth) and \
                        all(comp_id.rel_type in ['validated', 'done'] for comp_id in comp_with_meth) \
                        and len(num_with_meth) + len(comp_with_meth) >= len(meth_ids):
                    meth_dict = result_comp_obj.method_param_dict(num_ids, comp_ids)
                    computation_id.compute_state(meth_dict)

    def get_result_value(self, default_str='', options=False, lang=False):
        """
        Default function to get interpreted value for a type of result (str)
        :param default_str: if the function returns an empty value, return this string instead
        :return:
        """
        # Sometimes CA results don't have a date_result (when CA don't move to the value of 0.00)
        # Ex Nu = 1.00; Formula (Nu - 1.00 = Ca) but need to be printed in report
        if self.date_result or self.rel_type == 'done' or self.rel_type == 'validated':
            digits = (self.env['decimal.precision'].precision_get('Analysis Result') or 5) + 2
            value = float_round(self.value, precision_digits=digits)
            if options == 'raw':
                return value
            # Step 1
            prefix = ""
            loq_mode = False
            if not self.method_param_charac_id.not_check_loq:
                loq = float_round(self.loq, precision_digits=digits)
                if loq > value:
                    prefix = "< "
                    value = loq
                    loq_mode = True
                    # Step 2
            if not self.method_param_charac_id.not_check_max_value and not loq_mode:
                mloq = float_round(self.mloq, precision_digits=digits)
                if mloq < value:
                    prefix = "> "
                    value = mloq
                    loq_mode = True
            return "{}{}".format(prefix, self.format_result(value,
                                                            self.method_param_charac_id,
                                                            loq_mode=loq_mode,
                                                            lang=lang,
                                                            options=False))
        return default_str

    def add_specific_values(self, result_vals, lang=False):
        result_vals.update({
            'loq': self.format_result(self.loq, self.method_param_charac_id, lang=lang,
                                      loq_mode=True) if self.loq else False,
            'mloq': self.format_result(self.mloq, self.method_param_charac_id, lang=lang,
                                       loq_mode=True) if self.mloq else False,
            'u': self.format_result(self.u, self.method_param_charac_id, lang=lang) if self.u else False,
            'lod': self.format_result(self.lod, self.method_param_charac_id, lang=lang,
                                      loq_mode=True) if self.lod else False,
        })
        return result_vals

    def method_param_dict(self, num_ids, comp_ids):
        meth_dict = dict()
        for num_id in num_ids:
            meth_dict[num_id.method_param_charac_id] = ({
                'value': num_id.corrected_value if num_id.corrected_value else num_id.value,
                'loq': num_id.corrected_loq if num_id.corrected_loq else num_id.loq,
                'state': num_id.rel_type,
            })
        for comp_id in comp_ids:
            meth_dict[comp_id.method_param_charac_id] = ({
                'value': comp_id.value,
                'loq': comp_id.loq,
                'state': comp_id.rel_type,
            })
        return meth_dict

    def do_done(self, done_stage_id=False):
        res = super().do_done(done_stage_id)
        for cmp_id in self:
            numeric_ids = cmp_id.analysis_id.result_num_ids.filtered(
                lambda r: r.rel_type not in ['cancel', 'rework'])
            computation_ids = cmp_id.analysis_id.result_compute_ids.filtered(
                lambda r: r.rel_type != 'cancel' and r.correspondence_ids.filtered(
                    lambda x: x.method_param_charac_id == cmp_id.method_param_charac_id))
            check_both = lambda z: z.method_param_charac_id in meth_ids
            # Get all necessary result for computation (numeric and compute)
            cond_result_needed = lambda y: y.method_param_charac_id.id in computation_ids.correspondence_ids. \
                method_param_charac_id.ids
            num_ids = numeric_ids.filtered(cond_result_needed)
            comp_ids = cmp_id.analysis_id.result_compute_ids.filtered(cond_result_needed)
            for computation_id in computation_ids:
                meth_ids = computation_id.correspondence_ids.filtered(
                    lambda y: not y.is_optional).method_param_charac_id
                num_with_meth = num_ids.filtered(check_both)
                comp_with_meth = comp_ids.filtered(check_both)
                if all(num_id.rel_type in ['validated', 'done'] for num_id in num_with_meth) and \
                        all(comp_id.rel_type in ['validated', 'done'] for comp_id in comp_with_meth) \
                        and len(num_with_meth) + len(comp_with_meth) >= len(meth_ids):
                    meth_dict = cmp_id.method_param_dict(num_ids, comp_ids)
                    computation_id.compute_state(meth_dict)
        return res

    def prepare_result_log(self, log, result_reason_id=False):
        res = super().prepare_result_log(log, result_reason_id)
        res.update({
            'compute_result_id': self.id,
        })
        return res

    def get_float_value(self):
        return self.value
