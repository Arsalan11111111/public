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
from odoo import models, fields, exceptions, _, api
import math
from ..static.libraries import sigfig


class LimsAnalysisResult(models.AbstractModel):
    _name = 'lims.analysis.result'
    _description = 'Result'
    _rec_name = 'method_param_charac_id'
    _tracking_parent = 'analysis_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    accreditation_ids = fields.Many2many('lims.accreditation', string='Organisms', tracking=True,
                                         help="List of accreditations linked with this result.")
    accreditation = fields.Selection([('inta', 'Internal Accredited'), ('intna', ' Internal Not Accredited'),
                                      ('exta', 'External Accredited'), ('extna', 'External Not Accredited')],
                                     string='Accreditation Type', tracking=True, help="Type of accreditation of this result.")
    active = fields.Boolean('Active', default=True)
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', index=True, help="The analysis that contains this result.")
    change = fields.Boolean('Change', readonly=1, copy=False)
    comment = fields.Char('Comment', translate=True, tracking=True, help="This comment can be retrieved in many reports.")
    date_start = fields.Datetime('Date Start', index=True,
                                 help="This date is fulfilled only once at the moment when the analysis switch to 'WIP' stage.")
    date_result = fields.Datetime('Date Result', index=True)
    is_rework = fields.Boolean('Reworked', copy=False,
                               help="This is checked when the result switch to 'Re-work' stage.")
    method_id = fields.Many2one('lims.method', 'Method', related='sop_id.method_id', store=True, compute_sudo=True,
                                help="This is the method of the test that contain that result.")
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True,
                                             index=True)
    pack_id = fields.Many2one('lims.parameter.pack', 'Source Pack', index=True)
    show = fields.Boolean('Show on report', help="Show result's comment on report.")
    print_on_report = fields.Boolean('Print Result', default=True,
                                     help="If the printing system is well defined and if this option is checked then "
                                          "this result will be printed on the report.")
    sop_id = fields.Many2one('lims.sop', 'Test', index=True, ondelete='cascade',
                             help="This is the test that contain that result.")
    stage_id = fields.Many2one('lims.result.stage', string='Stage', copy=False)
    state = fields.Selection('get_selection_state', 'State', help="This is the state of the conformity of that result.")
    user_id = fields.Many2one('res.users', 'Operator Input', index=True)
    uom_id = fields.Many2one('uom.uom', 'UoM', tracking=True)

    rel_batch_id = fields.Many2one('lims.batch', related="sop_id.batch_id", store=True, compute_sudo=True,
                                   help="This is the batch of the test that contain that result.")
    rel_change_result = fields.Boolean(related='stage_id.change_result', readonly=True, compute_sudo=True,
                                       help="This is the 'Change result' of the stage of that result.")
    rel_date_sample = fields.Datetime(related="analysis_id.date_sample", string='Date Sample', store=True,
                                      compute_sudo=True, help="This is the 'Date sample' of the analysis.")
    rel_department_id = fields.Many2one(related='sop_id.department_id', store=True, readonly=True, compute_sudo=True,
                                        help="This is the department of the test that contain that result.")
    rel_laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', related='analysis_id.laboratory_id',
                                        store=True, help="This is the 'Laboratory' of the analysis.")
    rel_labo_users_ids = fields.Many2many('res.users', related="rel_laboratory_id.res_users_ids", string="Lab User",
                                          help="This is the 'Users' of the laboratory of the analysis.")
    rel_dept_user_ids = fields.Many2many('res.users', related="rel_department_id.res_users_ids", string="Dept User",
                                         help="This is the 'Users' of the department of the analysis.")
    rel_manage_accreditation = fields.Boolean(related='rel_laboratory_id.manage_accreditation', compute_sudo=True,
                                              help="This is the 'Manage accreditation on result' of the laboratory "
                                                   "of the analysis.")
    rel_matrix_id = fields.Many2one('lims.matrix', string='Matrix', related='analysis_id.matrix_id', store=True,
                                    compute_sudo=True, help="This is the 'Matrix' of the analysis.")
    rel_partner_id = fields.Many2one('res.partner', 'Partner', related='analysis_id.partner_id', store=True,
                                     compute_sudo=True, help="This is the 'Partner' of the analysis.")
    rel_request_id = fields.Many2one(related='analysis_id.request_id', string='Request', store=True, compute_sudo=True,
                                     help="This is the 'Request' of the analysis.")
    rel_type = fields.Selection(related='stage_id.type', store=False, compute_sudo=True, readonly=True,
                                help="This is the 'Type' of the stage of that result.")
    display_name_for_history = fields.Char()

    @api.model
    def get_selection_state(self):
        return [
            ('init', _('Init')),
            ('conform', _('Conform')),
            ('not_conform', _('Not Conform')),
            ('unconclusive', _('Inconclusive'))
        ]

    @api.model
    def get_state_translated(self, state_to_translate=False):
        """
        Get the state translated for a result used in Qweb or reports.
        :return:
        """
        if state_to_translate:
            return dict(self.get_selection_state())[state_to_translate]
        return dict(self.get_selection_state())[self.state] if self.state else False

    @api.model_create_multi
    def create(self, vals_list):
        """
        Compute the value of dilution factor, create the result, create the limits for this result
        :param vals_list:
        :return:
        """
        param_obj = self.env['lims.method.parameter.characteristic'].sudo()
        ana_obj = self.env['lims.analysis'].sudo()
        method_param_charac_ids = param_obj.search(
            [('id', 'in', [val.get('method_param_charac_id') for val in vals_list])])
        analysis_ids = ana_obj.search([('id', 'in', [val.get('analysis_id') for val in vals_list])])
        for vals in vals_list:
            method_param_charac_id = method_param_charac_ids.filtered(lambda x: x.id == vals.get(
                'method_param_charac_id'))
            vals = self.add_parameter_values(method_param_charac_id, vals)
            if vals.get('analysis_id'):
                analysis_id = analysis_ids.filtered(lambda x: x.id == vals.get('analysis_id'))
                vals = self.add_analysis_values(analysis_id, vals)
        return super(LimsAnalysisResult, self).create(vals_list)

    def do_plan(self, plan_stage_id=False):
        """
        Pass the result in stage "plan"
        :return:
        """
        if not plan_stage_id:
            plan_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'plan')], limit=1)
        if plan_stage_id:
            self.write({
                'stage_id': plan_stage_id.id,
            })
        else:
            raise exceptions.ValidationError(_('No result stage "plan" found'))

    def do_todo(self, todo_stage_id=False):
        """
        Pass the result in stage "todo"
        :return:
        """
        if not todo_stage_id:
            todo_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'todo')], limit=1)
        if todo_stage_id:
            self.write({
                'stage_id': todo_stage_id.id,
            })
        else:
            raise exceptions.ValidationError(_('No result stage "todo" found'))

    def do_wip(self, wip_stage_id=False):
        """
        Pass the result in stage "wip"
        :return:
        """
        if not wip_stage_id:
            wip_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'wip')], limit=1)
        if wip_stage_id:
            self.write({
                'stage_id': wip_stage_id.id,
            })
            self.filtered(lambda r: not r.date_start).write({'date_start': fields.Datetime.now()})
        else:
            raise exceptions.ValidationError(_('No result stage "wip" found'))

    def do_done(self, done_stage_id=False):
        """
        Pass the result in stage "done", check if the sop could pass in stage "done"
        :return:
        """
        if not done_stage_id:
            done_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'done')], limit=1)
        if done_stage_id:
            self.sop_id.filtered(lambda s: s.stage_id.type == 'todo').do_wip()
            self.write({
                'stage_id': done_stage_id.id,
            })
            self.check_result_conformity()
            self.sop_id.check_sop_state()
            self.sop_id.check_results_done()
            self.filtered(lambda r: r.method_param_charac_id.auto_valid).do_validated()
        else:
            raise exceptions.ValidationError(_('No stage result "done" found'))

    def do_validated(self, validated_stage_id=False):
        """
        Pass the result in stage "validated", check if the SOP could pass in stage "validated"
        :return:
        """
        if not validated_stage_id:
            validated_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'validated')], limit=1)
        if validated_stage_id:
            self.write({
                'stage_id': validated_stage_id.id,
            })
            self.sop_id.check_state_validated()
        else:
            raise exceptions.ValidationError(_('No stage result "validated" found'))

    def add_parameter_values(self, method_param_charac_id, vals):
        vals.update({
            'accreditation': method_param_charac_id.accreditation,
            'accreditation_ids': [(6, 0, method_param_charac_id.accreditation_ids.ids)],
            'print_on_report': method_param_charac_id.parameter_id.is_default_print_on_report,
            'uom_id': method_param_charac_id.uom.id,
        })
        return vals

    def add_analysis_values(self, analysis_id, vals):
        vals.update({
            'show': analysis_id.laboratory_id.sudo().show_result_comment,
        })
        return vals

    def check_result_conformity(self):
        """
        Conformity checks, if available, change according to the type of result
        """
        return True

    def unlink(self):
        if not self.env.context.get('bypass_checks'):
            to_recompute_ids = self.env['lims.analysis.compute.result']
            wip_stage_id = self.env['lims.result.stage'].search([('type', '=', 'wip')], limit=1)
            for record in self:
                record.sop_id.message_post(body=_('Result with parameter: {} removed by {}').format(
                    record.method_param_charac_id.display_name, self.env.user.name))
                record.analysis_id.message_post(body=_('Result with parameter: {} removed by {}').format(
                    record.method_param_charac_id.display_name, self.env.user.name))
                result_compute = record.analysis_id.result_compute_ids.filtered(
                    lambda c: c.rel_type != 'cancel' and
                              record.method_param_charac_id in c.correspondence_ids.method_param_charac_id)
                to_recompute_ids |= result_compute.filtered(lambda c: c.correspondence_ids.filtered(
                    lambda co: co.method_param_charac_id == record.method_param_charac_id).is_optional)
                to_reset_compute = result_compute - to_recompute_ids

                to_reset_compute.write({'value': 0, 'state': 'init', 'stage_id': wip_stage_id.id})
            analysis_ids = self.analysis_id
            sop_ids = self.sop_id
            res = super().unlink()
            analysis_ids.clean_packs()
            for compute_id in to_recompute_ids:
                cond_result_needed = lambda y: y.method_param_charac_id.id in compute_id.correspondence_ids. \
                    method_param_charac_id.ids
                num_ids = compute_id.analysis_id.result_num_ids.filtered(cond_result_needed)
                comp_ids = compute_id.analysis_id.result_compute_ids.filtered(cond_result_needed)
                meth_ids = compute_id.correspondence_ids.filtered(lambda y: not y.is_optional).method_param_charac_id
                check_both = lambda z: z.method_param_charac_id in meth_ids
                if all(num_id.rel_type in ['validated', 'done'] for num_id in num_ids.filtered(check_both)) and \
                        all(comp_id.rel_type in ['validated', 'done'] for comp_id in comp_ids.filtered(check_both)) \
                        and len(num_ids) + len(comp_ids) >= len(meth_ids):
                    meth_dict = to_recompute_ids.method_param_dict(num_ids, comp_ids)
                    compute_id.compute_state(meth_dict)
            self._post_actions_on_unlink_or_cancel(sop_ids)
        else:
            res = super().unlink()
        return res

    def do_cancel(self, cancel_stage_id=False):
        cancel_stage_id = cancel_stage_id or self.env['lims.result.stage'].sudo().search([
            ('type', '=', 'cancel')
        ], limit=1)
        if cancel_stage_id:
            self.write({
                'stage_id': cancel_stage_id.id,
            })
            self._post_actions_on_unlink_or_cancel()
            self.reset_compute_result()
        else:
            raise exceptions.ValidationError(_('No result stage "cancel" found'))

    def do_rework(self, rework_reason='', rework_stage_id=False):
        """
        Copy the result, the result pass in stage "rework",
        the sop pass in stage "todo", the analysis pass in stage "wip",
        the request pass in state "wip", reload the page
        :return:
        """
        rework_stage_id = rework_stage_id or self.env['lims.result.stage'].sudo().search([
            ('type', '=', 'rework')
        ], limit=1)
        if rework_stage_id:
            for record in self:
                new_result = record.copy(default=record.get_vals_rework())
                record.stage_id = rework_stage_id.id,
                record.sop_id.do_todo()
                record.analysis_id.sudo().do_wip()
                if record.analysis_id.request_id:
                    record.analysis_id.request_id.sudo().state = 'in_progress'
                record.is_rework = True

                new_result.write({
                    'comment': 'Rework reason : {0}'.format(rework_reason) if rework_reason else ''
                })
            self.sop_id.write({'has_rework': True})
            self.reset_compute_result()
        else:
            raise exceptions.ValidationError(_('No result stage "rework" found'))
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

    def reset_compute_result(self):
        result_comp_obj = self.env['lims.analysis.compute.result']
        for record in self:
            if record.analysis_id.result_compute_ids:
                result_compute = record.analysis_id.result_compute_ids.filtered(lambda c: c.rel_type != 'cancel')
                compute_ids = result_compute.filtered(
                    lambda c: record.method_param_charac_id in c.correspondence_ids.mapped('method_param_charac_id'))
                mandatory_compute_ids = compute_ids \
                    .filtered(lambda r: not r.correspondence_ids.
                              filtered(lambda c: c.method_param_charac_id == record.method_param_charac_id).is_optional)
                if mandatory_compute_ids:
                    mandatory_compute_ids.write({'value': 0, 'state': 'init'})
                    mandatory_compute_ids.do_todo()
                    mandatory_compute_ids.sop_id.do_todo()
                    mandatory_compute_ids.analysis_id.do_wip()
                elif compute_ids:
                    for compute_id in compute_ids:
                        cond_result_needed = lambda y: y.method_param_charac_id.id in compute_id.correspondence_ids. \
                            method_param_charac_id.ids
                        num_ids = record.analysis_id.result_num_ids.filtered(cond_result_needed)
                        comp_ids = record.analysis_id.result_compute_ids.filtered(cond_result_needed)
                        meth_ids = compute_id.correspondence_ids.filtered(
                            lambda y: not y.is_optional).method_param_charac_id
                        check_both = lambda z: z.method_param_charac_id in meth_ids
                        if all(num_id.rel_type in ['validated', 'done'] for num_id in num_ids.filtered(check_both)) and \
                                all(comp_id.rel_type in ['validated', 'done'] for comp_id in comp_ids.filtered(check_both)) \
                                and len(num_ids) + len(comp_ids) >= len(meth_ids):
                            meth_dict = result_comp_obj.method_param_dict(num_ids, comp_ids)
                            compute_id.compute_state(meth_dict)

    def get_vals_rework(self):
        todo_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'todo')], limit=1)
        return {
            'is_rework': True,
            'stage_id': todo_stage_id.id,
            'date_start': False,
            'state': False,
            'user_id': False,
        }

    def get_form_view_of_result(self):
        return {
            'name': _('View Form'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def get_limit_result_ids(self):
        """
        Return the limit (function overwrite in other module)
        :return:
        """
        return self.method_param_charac_id.limit_ids

    def get_result_value(self, default_str='', options=False, lang=False):
        """
        Default function to get interpreted value for a type of result (str)
        Must be overloaded in each type of result
        :param default_str: if the function returns an empty value, return this string instead
        :return:
        """
        return default_str

    @staticmethod
    def sigfig_decimal(input_value, n_decimal=2, sep_dec='.', sep_tho='', output_type=str):
        """
        Get decimal from float value
        :param input_value:
        :param n_decimal:
        :param sep_dec:
        :param sep_tho:
        :param output_type:
        :return:
        """
        output_value = sigfig.round(input_value, decimals=n_decimal, decimal=sep_dec, spacer=sep_tho, output_type=str)
        return output_value

    @staticmethod
    def sigfig_significant(input_value, n_significant=4, sep_dec='.', sep_tho='', output_type=str):
        """
        Get significant from a float value
        :param input_value:
        :param n_significant:
        :param sep_dec:
        :param sep_tho:
        :param output_type: str or float
        :return:
        """
        output_value = sigfig.round(input_value, sigfigs=n_significant, decimal=sep_dec, spacer=sep_tho,
                                    output_type=str)
        return output_value

    @staticmethod
    def sigfig_uncertainty(input_value, u_value, sep_dec='.', sep_tho='', output_type=str):
        """
        Get value with a combination of Value +- u (can be in string or list or tuple)
        :param input_value:
        :param u_value:
        :param sep_dec:
        :param sep_tho:
        :param output_type: str
        :return:
        """
        output_value = sigfig.round(input_value, uncertainty=u_value, decimal=sep_dec, spacer=sep_tho, output_type=str)
        return output_value

    def sigfig_format(self, input_value, method='decimal', n_decimal=2, n_significant=4, sep_dec='.', sep_tho='',
                      input_u=0.0, output_type=str):
        """
        Get the right mode for sigfigs
        :param input_value:
        :param method:
        :param n_decimal:
        :param n_significant:
        :param sep_dec:
        :param sep_tho:
        :param input_u:
        :param output_type:
        :return:
        """
        if method == 'both':
            exp_value = math.floor(math.log10(abs(input_value))) if input_value != 0 else 0
            if exp_value - n_significant < -n_decimal:
                method = 'decimal'
            else:
                method = 'significant_figure'
        if method == 'decimal':
            input_value = self.sigfig_decimal(input_value, n_decimal, sep_dec, sep_tho, output_type)
        elif method == 'significant_figure':
            input_value = self.sigfig_significant(input_value, n_significant, sep_dec, sep_tho, output_type)
        elif method == 'uncertainty' and input_u != 0.0:
            input_value = self.sigfig_uncertainty(input_value, input_u, sep_dec, sep_tho, output_type)
        return input_value

    def format_result(self, value, method_parameter_charac, lang=False, input_u=0.0, loq_mode=False, options=False):
        """ Mainly used in qwebs
        :param value: the value of the result with X decimal
        :param method_parameter_charac: the method parameter charac of the result
        :param lang: lang of the qweb partner
        :param input_u: For _sigfig_uncertainty() function : u value in float from result (or parameter characteristic)
        :param loq_mode: Set mode 'decimal' and significant_number_loq_showed as parameter
        :return:
        """
        if loq_mode:
            n_decimal = method_parameter_charac.decimal_loq_showed
            method = 'decimal'
        else:
            method = method_parameter_charac.format_number_report
            n_decimal = method_parameter_charac.nbr_dec_showed
        n_significant = method_parameter_charac.significant_figure
        language = self.env['res.lang'].search([('code', '=', lang)])
        sep_dec = language.decimal_point if language.decimal_point else '.'
        sep_tho = language.thousands_sep if language.thousands_sep else ''
        value = self.sigfig_format(value, method, n_decimal, n_significant, sep_dec, sep_tho, input_u)
        return value

    def add_specific_values(self, result_vals, lang=False):
        """
        Function to be inherited on specific results types is some fields relatives to this specific type must be added
        to the result reporting dictionary
        """
        return result_vals

    def open_wizard_history(self):
        self.ensure_one()
        res = {
            'name': _('History'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'lims.history',
            'context': {'default_method_param_charac_id': self.method_param_charac_id.id,
                        'default_partner_id': self.analysis_id.partner_id.id,
                        'default_product_id': self.analysis_id.product_id.id,
                        'default_batch_id': self.rel_batch_id.id,
                        'default_user_id': self.user_id.id,
                        'force_write': True},
            'target': 'new',
        }

        return res

    def prepare_result_log(self, log, result_reason_id=False):
        vals = {
            'user_id': self.env.uid,
            'log': log,
            'date': fields.Datetime.now(),
        }
        if result_reason_id:
            vals.update({
                'result_reason_id': result_reason_id
            })
        return vals

    def record_changes(self, parameter_name, change_type, before_name, after_name):
        if self.env.context.get('accreditation'):
            body = _("Result with parameter: {} {} change into {} by {}").format(
                parameter_name, change_type, before_name, after_name)
        else:
            body = _("Result with parameter: {} change {} from {} to {}").format(
                parameter_name, change_type, before_name, after_name)
        return self.analysis_id.message_post(body=body)

    def check_department(self):
        if set(self.sop_id.department_id.ids) - set(self.env.user.department_ids.ids):
            raise exceptions.AccessError(_("You can only encode results from your department"))

    def get_result_uom(self):
        """
        Global function must be overloaded by other results if uom_id is set.
        :param default_str:
        :return:
        """
        return self.uom_id

    def _post_actions_on_unlink_or_cancel(self, sop_ids=False):
        if not sop_ids:
            sop_ids = self.sop_id
        sop_ids.check_results_done()
        # if all parameters are auto_valid and all remaining parameters are validated, sop shouldn't pass in 'done'
        # state
        auto_validate_sop = sop_ids.filtered(lambda s: s.rel_type != 'cancel' and all(
            [method_param_id.auto_valid for method_param_id in s.get_all_params()]))
        if auto_validate_sop:
            auto_validate_sop.check_state_validated()
        sop_ids.check_sop_state()

    def get_result_vals(self):
        """
        Add vals after result creation from request (reason = analysis is not set on result creation)
        To be overridden on specific results or on other modules
        """
        self.ensure_one()
        return {'show': self.rel_laboratory_id.sudo().show_result_comment}

    def get_float_value(self):
        return 0.0
