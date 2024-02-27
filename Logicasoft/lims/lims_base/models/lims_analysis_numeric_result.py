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
from odoo import fields, models, api, exceptions, _, Command
from odoo.tools.float_utils import float_compare, float_round


class LimsAnalysisNumericResult(models.Model):
    _name = 'lims.analysis.numeric.result'
    _description = 'Numerical analysis result'
    _inherit = ['lims.analysis.result']

    rel_sample_name = fields.Char('Sample Name', related='analysis_id.sample_name', store=True, compute_sudo=True,
                                  help="This is the sample name of the analysis that contains that result.")
    value = fields.Float('Value', digits='Analysis Result', tracking=True)
    corrected_value = fields.Float('Corrected Value', digits='Analysis Result',
                                   compute='compute_corrected_value', store=True, compute_sudo=True,
                                   help="It is equal to the multiplication of the value of the result and his dilution "
                                        "factor.")
    is_null = fields.Boolean(tracking=True)
    loq = fields.Float('LOQ', digits='Analysis Result', tracking=True)
    corrected_loq = fields.Float('Corrected LOQ', digits='Analysis Result', compute='compute_corrected_value',
                                 store=True, compute_sudo=True, help="It is equal to the multiplication of the 'LOQ' "
                                                                     "of the result and his dilution factor.")
    u = fields.Float('U', digits='Analysis Result')
    corrected_u = fields.Float('Corrected U', digits='Analysis Result', compute='compute_corrected_value',
                               compute_sudo=True, help="It is equal to the multiplication of the 'U' of the result and "
                                                       "his dilution factor.")
    ls = fields.Float('LS', digits='Analysis Result')
    lod = fields.Float('LOD', digits='Analysis Result')
    corrected_lod = fields.Float('Corrected LOD', digits='Analysis Result', compute='compute_corrected_value',
                                 compute_sudo=True, help="It is equal to the multiplication of the 'LOD' of the result "
                                                         "and his dilution factor.")
    mloq = fields.Float('mLOQ', digits='Analysis Result')
    corrected_mloq = fields.Float('Corrected mLOQ', digits='Analysis Result', compute='compute_corrected_value',
                                  compute_sudo=True, help="It is equal to the multiplication of the 'mLOQ' of the result "
                                                          "and his dilution factor.")
    result_log_ids = fields.One2many('lims.result.log', 'result_id', readonly=1)
    limit_result_ids = fields.One2many('lims.analysis.limit.numeric.result', 'result_id')
    decision_limit_result_id = fields.Many2one('lims.analysis.limit.numeric.result', copy=False,
                                               help="The chosen limit that is finally taken for the conformity.")
    result_reason_id = fields.Many2one('lims.result.reason', 'Reason', copy=False)
    recovery = fields.Float('Recovery', digits='Analysis Result')
    dilution_factor = fields.Float(string='Dil. Fact.', default=1, digits='Analysis Result', tracking=True)
    is_alert = fields.Boolean(copy=False, help="This is checked if the result get a decision on his conformity "
                                               "that lead to an alert.")
    rel_change_loq = fields.Boolean(related='analysis_id.laboratory_id.change_loq', readonly=True, compute_sudo=True,
                                    help="This is the 'Change LOQ' checkbox of the laboratory of the analysis.")

    def set_is_null(self):
        """
        Set is_null True if records are wip and validate = 0
        :return:
        """
        self.filtered(lambda r: r.rel_type == 'wip' and r.value == 0).write({'is_null': True})

    def add_parameter_values(self, method_param_charac_id, vals):
        vals = super(LimsAnalysisNumericResult, self).add_parameter_values(method_param_charac_id, vals)
        vals.update({
            'loq': method_param_charac_id.loq,
            'mloq': method_param_charac_id.mloq,
            'lod': method_param_charac_id.lod,
            'u': method_param_charac_id.u,
            'ls': method_param_charac_id.ls,
            'recovery': method_param_charac_id.recovery,
        })
        return vals

    def add_analysis_values(self, analysis_id, vals):
        vals.update({
            'dilution_factor': analysis_id.dilution_factor or 1,
        })
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """
        Compute the value of dilution factor, create the result, create the limits for this result
        :param vals_list:
        :return:
        """
        res = super().create(vals_list)
        if not self.env.context.get('no_limit'):
            res.sudo().create_limit_result() 
        return res

    def create_limit_result(self):
        """
        Create the limits for the result
        :return:
        """
        for record in self:
            limit_ids = record.sudo().get_limit_result_ids()
            record.create_limit(limit_ids)
            if not limit_ids.filtered(lambda l: l.type_alert == 'limit') and \
                    record.method_param_charac_id.limit_ids and \
                    record.method_param_charac_id.limit_ids.filtered(lambda l: l.type_alert == 'limit'):
                record.create_limit(record.method_param_charac_id.limit_ids.filtered(lambda l: l.type_alert == 'limit'))

    def create_limit(self, limit_ids):
        result_limit_obj = self.env['lims.analysis.limit.numeric.result']
        for limit in limit_ids:
            vals = self.get_limit_vals(limit)
            self.limit_result_ids += result_limit_obj.create(vals)

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
            'result_id': self.id,
        }
        return vals

    @api.depends('value', 'dilution_factor', 'loq', 'u', 'lod', 'mloq')
    def compute_corrected_value(self):
        """
        Compute the corrected value
        :return:
        """
        self = self.sudo()
        for record in self:
            record.corrected_value = record.value * record.dilution_factor
            record.corrected_loq = record.loq * record.dilution_factor
            record.corrected_u = record.u * record.dilution_factor
            record.corrected_lod = record.lod * record.dilution_factor
            record.corrected_mloq = record.mloq * record.dilution_factor

    def onchange_dilution_factor(self):
        """
        Check if dilution factor >= 0 and <= dilution factor max present in the laboratory
        :return:
        """
        self = self.sudo()
        digits = self.env['decimal.precision'].precision_get('Analysis Result') + 2
        for record in self:
            dilution_max = float_round(record.analysis_id.laboratory_id.dilution_factor_max, precision_digits=digits)
            dilution_record = float_round(record.dilution_factor, precision_digits=digits)
            if not (0 < dilution_record <= dilution_max):
                raise exceptions.ValidationError(
                    _('Factor could not be below / equal 0 or greater than {}, '
                      'as defined in the Lab configuration.').format(dilution_max))

    @api.constrains('is_null', 'value')
    def check_is_null_value(self):
        """
        Check if the result is null and value is != 0 in the same time
        :return:
        """
        for record in self:
            if record.is_null and record.value:
                raise exceptions.ValidationError(_('Result {} has both value and is null completed.')
                                                 .format(record.method_param_charac_id.tech_name))

    def write(self, vals):
        """
        Write the record, Set the user in user_id, check dilution factor, check if result could pass in stage "done",
        Check conformity of the result, Check if result is related to compute result, Check state of the analysis
        :param vals:
        :return:
        """
        if not self.env.context.get('bypass'):
            digits = self.env['decimal.precision'].precision_get('Analysis Result')
            if ('value' in vals or 'is_null' in vals) and not self.env.su:
                self.check_department()
                if not vals.get('user_id'):
                    vals.update({'user_id': self.env.user.id})
                if not vals.get('date_result'):
                    vals.update({'date_result': fields.Datetime.now()})
            if vals.get('result_reason_id'):
                vals.update({'change': True})
            if vals.get('value') and all(self.mapped(
                    lambda r: float_compare(float(vals.get('value')), r.value, digits) == 0
            )):
                del vals['value']
            for record in self:
                if 'value' in vals or 'is_null' in vals and vals.get('is_null') != record.is_null:
                    log = _('Old value: {} | New value: {}').format((round(record.value, digits) or
                                                                     record.is_null and '0') if record.state else '-',
                                                                    vals.get('is_null') and '0' or
                                                                    round(float(vals.get('value', 0)), digits))
                    result_log = record.prepare_result_log(log,
                                                           vals.get('result_reason_id') or record.result_reason_id.id)
                    self.env['lims.result.log'].create(result_log)
        res = super(LimsAnalysisNumericResult, self).write(vals)
        if not self.env.context.get('bypass'):
            if vals.get('value') or vals.get('is_null'):
                self.do_done()
            if vals.get("dilution_factor"):
                self.onchange_dilution_factor()
                result_ids = self.filtered(lambda r: r.rel_type == 'validated')
                if result_ids:
                    result_ids.do_done()
        return res

    def check_result_conformity(self):
        """
        Check conformity of the result
        :return:
        """
        for record in self:
            value = record.corrected_value
            if value or record.is_null:
                limit_id = record.sudo().get_result_limit(value)
                record.sudo().write({'state': limit_id.state if limit_id else 'init',
                                     'decision_limit_result_id': limit_id.id if limit_id else False,
                                     'is_alert': True if limit_id and limit_id.type_alert == 'alert' else False})

    def get_result_limit(self, value, custom_limits=False):
        self.ensure_one()
        digits = self.env['decimal.precision'].precision_get('Analysis Result')
        for limit in (custom_limits or self.limit_result_ids):
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

    def open_cancel(self):
        return {
            'name': 'Cancel result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.cancel.wizard',
            'context': {'default_result_ids': self.ids},
            'target': 'new',
        }

    def do_cancel(self, cancel_stage_id=False):
        """
        Pass the result in stage "cancel"
        :return:
        """
        super(LimsAnalysisNumericResult, self).do_cancel(cancel_stage_id)
        self = self.sudo()
        for record in self:
            log = _('Result is cancelled')
            self.env['lims.result.log'].create({
                'result_id': record.id,
                'user_id': self.env.uid,
                'log': log,
                'date': fields.Datetime.now()
            })
            record.change = True

    def open_wizard_mass_change_result(self):
        """
        Open the wizard for mass change on result
        :return:
        """
        return {
            'name': 'Mass Change Result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mass.change.result.wizard',
            'context': {'default_analysis_result_ids': self.ids},
            'target': 'new',
        }

    def open_rework(self):
        return {
            'name': 'Rework result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.rework.wizard',
            'context': {'default_result_ids': self.ids},
            'target': 'new',
        }

    def do_rework(self, rework_reason='', rework_stage_id=False):
        res = super(LimsAnalysisNumericResult, self).do_rework(rework_reason, rework_stage_id)
        self.reset_compute_result()
        return res

    def reset_compute_result(self):
        result_comp_obj = self.env['lims.analysis.compute.result']
        for record in self:
            if record.analysis_id.result_compute_ids:
                result_compute = record.analysis_id.result_compute_ids.filtered(lambda c: c.rel_type != 'cancel')
                compute_ids = result_compute.filtered(
                    lambda c: record.method_param_charac_id in c.correspondence_ids.mapped('method_param_charac_id'))
                mandatory_compute_ids = compute_ids.filtered(lambda r: not r.correspondence_ids.filtered(
                    lambda c: c.method_param_charac_id == record.method_param_charac_id and c.is_optional))
                if mandatory_compute_ids:
                    mandatory_compute_ids.write({'value': 0, 'state': 'init'})
                    mandatory_compute_ids.do_todo()
                    mandatory_compute_ids.sop_id.do_todo()
                    mandatory_compute_ids.analysis_id.do_wip()
                elif compute_ids:
                    for compute_id in compute_ids:
                        cond_result_needed = lambda y: y.method_param_charac_id.id in compute_id.correspondence_ids. \
                            method_param_charac_id.ids
                        num_ids = record.analysis_id.result_ids.filtered(cond_result_needed)
                        comp_ids = record.analysis_id.result_compute_ids.filtered(cond_result_needed)
                        meth_ids = record.correspondence_ids.filtered(
                            lambda y: not y.is_optional).method_param_charac_id
                        check_both = lambda z: z.method_param_charac_id in meth_ids
                        if all(num_id.rel_type in ['validated', 'done'] for num_id in num_ids.filtered(check_both)) and \
                                all(comp_id.rel_type in ['validated', 'done'] for comp_id in
                                    comp_ids.filtered(check_both)) \
                                and len(num_ids) + len(comp_ids) >= len(meth_ids):
                            meth_dict = result_comp_obj.method_param_dict(num_ids, comp_ids)
                            record.compute_state(meth_dict)

    def get_vals_rework(self):
        vals = super(LimsAnalysisNumericResult, self).get_vals_rework()
        vals.update({
            'value': 0,
            'is_null': False,
            'corrected_value': 0,
            'result_reason_id': False
        })
        return vals

    def check_computed_result(self):
        """
        Check for compute the compute_result
        :return:
        """
        self.env['lims.analysis.compute.result'].check_computed_result(self)
            
    def do_done(self, done_stage_id=False):
        res = super(LimsAnalysisNumericResult, self).do_done(done_stage_id)
        self.check_computed_result()
        return res

    def get_result_value(self, default_str='', options=False, lang=False):
        """
        Default function to get interpreted value for a type of result (str)
        :param default_str: if the function returns an empty value, return this string instead
        :return:
        """
        if self.corrected_value or self.is_null:
            # Evaluate is_null as number
            digits = (self.env['decimal.precision'].precision_get('Analysis Result') or 5) + 2
            corrected_value = 0.0 if self.is_null else float_round(self.corrected_value, precision_digits=digits)
            if options == 'raw':
                return corrected_value
            # Step 1
            prefix = ""
            loq_mode = False
            if not self.method_param_charac_id.not_check_loq:
                corrected_loq = float_round(self.corrected_loq, precision_digits=digits)
                if corrected_loq > corrected_value:
                    prefix = "< "
                    corrected_value = corrected_loq
                    loq_mode = True
            # Step 2
            if not self.method_param_charac_id.not_check_max_value and not loq_mode:
                corrected_mloq = float_round(self.corrected_mloq, precision_digits=digits)
                if corrected_mloq < corrected_value:
                    prefix = "> "
                    corrected_value = corrected_mloq
                    loq_mode = True
            return "{}{}".format(prefix, self.format_result(corrected_value,
                                                            self.method_param_charac_id,
                                                            loq_mode=loq_mode,
                                                            lang=lang,
                                                            options=False))
        return default_str

    def add_specific_values(self, result_vals, lang=False):
        result_vals.update({
            'loq': self.format_result(self.corrected_loq, self.method_param_charac_id,
                                      lang=lang, loq_mode=True) if self.corrected_loq else False,
            'mloq': self.format_result(self.corrected_mloq, self.method_param_charac_id,
                                       lang=lang, loq_mode=True) if self.corrected_mloq else False,
            'u': self.format_result(self.corrected_u, self.method_param_charac_id,
                                    lang=lang) if self.corrected_u else False,
            'lod': self.format_result(self.corrected_lod, self.method_param_charac_id,
                                      lang=lang, loq_mode=True) if self.corrected_u else False,
        })
        return result_vals

    def prepare_result_log(self, log, result_reason_id=False):
        res = super().prepare_result_log(log, result_reason_id)
        res.update({
            'result_id': self.id,
        })
        return res

    def get_result_vals(self, limits):
        res = super().get_result_vals()
        res.update({
            'limit_result_ids': [Command.create(limit.get_values()) for limit in limits]
        })
        return res

    def get_float_value(self):
        return self.corrected_value
