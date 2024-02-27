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
import contextlib
from odoo import fields, models, api, exceptions, _, Command
from odoo.tools import html2plaintext
from odoo.tools.misc import formatLang
from html.entities import html5


def timedelta_to_hours(time_to_convert):
    day = time_to_convert.days
    seconds = time_to_convert.seconds
    return day * 24 + seconds / 3600


class LimsAnalysis(models.Model):
    _name = 'lims.analysis'
    _description = 'Analysis'
    _order = 'id desc'
    _date_name = 'date_plan'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def get_default_stage(self):
        default_stage = self.env['ir.config_parameter'].sudo().get_param('analysis_stage_id')
        if default_stage and eval(default_stage):
            return int(default_stage)

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].sudo().search([('default_laboratory', '=', True)])
        return labo_id

    active = fields.Boolean('Active', default=True, tracking=True, help="Check this to archive the analysis.")
    category_id = fields.Many2one('lims.analysis.category', 'Category', index=True, tracking=True)
    reason_id = fields.Many2one('lims.analysis.reason', 'Reason', tracking=True)
    result_num_ids = fields.One2many('lims.analysis.numeric.result', 'analysis_id', string='Numerical Results',
                                     help="A list of the numerical results of the analysis.")
    result_sel_ids = fields.One2many('lims.analysis.sel.result', 'analysis_id', string='Selection Results',
                                     help="A list of the selection results of the analysis.")
    result_compute_ids = fields.One2many('lims.analysis.compute.result', 'analysis_id', 'Computed Results',
                                         help="A list of the compute results of the analysis.")
    result_text_ids = fields.One2many('lims.analysis.text.result', 'analysis_id', 'Text Results',
                                      help="A list of the text results of the analysis.")
    date_start = fields.Datetime('Analysis Start Date', index=True, copy=False, tracking=True,
                                 help="This date is fulfilled only once at the moment when the analysis switch to 'WIP' stage.")
    date_done = fields.Datetime('Analysis Done Date', index=True, copy=False, tracking=True,
                                help="This date is fulfil at the moment when the analysis switch to 'Done' stage.")
    date_plan = fields.Datetime('Date Plan', index=True,
                                help="This date is mandatory to planify the analysis and continue the process.")
    date_sample = fields.Datetime('Date Sample', index=True, tracking=True,
                                  help="This date is used to set the moment when the sample has been done.")
    date_report = fields.Datetime('Date Report', index=True,
                                  help="This date is fulfil only once at the moment you use the 'Preview HTML', 'Preview PDF' or 'Print' button.")
    rel_matrix_type_id = fields.Many2one(related='matrix_id.type_id', store=True,
                                         help="This is the related's type of the matrix of the analysis.")
    matrix_id = fields.Many2one('lims.matrix', 'Matrix', index=True, tracking=True, required=True,
                                help="This is the matrix of the analysis, which can be limited by the regulation.")
    matrix_id_domain_ids = fields.Many2many('lims.matrix', compute='compute_matrix_id_domain_ids')
    name = fields.Char('Name', readonly=True, index=True,
                       help="The name of the analysis is automatically set by the analysis's sequence set in the laboratory.")
    note = fields.Text('External comment',
                          help='Additional comment addressed to the customer (will be printed on analysis report)')
    partner_id = fields.Many2one('res.partner', 'Customer', required=False, index=True, tracking=True,
                                 help="The client of this analysis.")
    customer_ref = fields.Char('Reference', tracking=True, help="The reference of the client of this analysis.")
    sample_name = fields.Char('Sample Name', tracking=True, help="The name of sample.")
    date_sample_receipt = fields.Datetime('Date Sample Receipt', copy=False, tracking=True,
                                          help="This date is used to set the moment when the sample has been received.")
    state = fields.Selection('get_selection_state', 'State', index=True, help="The conformity state of the analysis.")
    stage_id = fields.Many2one('lims.analysis.stage', 'Stage', default=get_default_stage, tracking=True,
                               index=True, help="The progress of the analysis.")
    rel_type = fields.Selection(related='stage_id.type', readonly=1, store=False,
                                help="The name of the actuel progression's state of the analysis.")
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', required=True, default=get_default_laboratory,
                                    tracking=True, help="The laboratory of the analysis.")
    rel_labo_users_ids = fields.Many2many('res.users', related="laboratory_id.res_users_ids",
                                          help="The related's users of the laboratory of the analysis.")
    parent_id = fields.Many2one('lims.analysis', 'Parent Analysis', help="The parent analysis of this analysis.")
    regulation_id = fields.Many2one('lims.regulation', 'Regulation', tracking=True,
                                    help="This is the regulation of the analysis, which can be limited by the matrix.")
    regulation_id_domain_ids = fields.Many2many('lims.regulation', compute='compute_regulation_id_domain_ids')
    description = fields.Char('Description', help="A description of the analysis.")
    ref_sample_id = fields.Many2one('lims.analysis.request.sample', 'Parent sample',
                                    help="The sample linked to the analysis.")
    is_duplicate = fields.Boolean(help="This is checked if this analysis is a duplication or a rework of another analysis, which will become his parent analysis.")
    request_id = fields.Many2one('lims.analysis.request', 'Request', index=True, tracking=True, readonly=True,
                                 help="The request linked of this analysis.")
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler', index=True, tracking=True,
                                 domain=[('is_sampler', '=', True)],
                                 help="The public employee which will be the sampler of the analysis.")
    sop_ids = fields.One2many('lims.sop', 'analysis_id', 'Test', index=True, help="The tests of the analysis.")
    nb_sop = fields.Integer('NB Test', compute='compute_nb_sop', help="The number of tests of the analysis.")
    display_calendar = fields.Char(compute='get_display_name_calendar', help="The name shown in the calendar view.")
    is_incomplete = fields.Boolean('Incomplete', compute='compute_is_incomplete', store=True, copy=False,
                                   help="This is checked if one the the results of the analysis is on a 'cancel' state, or if the number of parameters of all his results is different from the parameters on the analysis and of his packs combined.")
    due_date = fields.Datetime('Due Date', index=True, tracking=True, copy=False,
                               help="This is the due date of the analysis.")
    cancel_reason = fields.Char(default='', tracking=True, copy=False,
                                help="This is the reason for which you have cancelled the analysis.")
    report_done = fields.Boolean('Report Done')
    dilution_factor = fields.Float(string='Dilution Factor', default=1, copy=False)
    tag_ids = fields.Many2many('lims.analysis.tag')
    external_sampling = fields.Boolean('Sampling By Customer', tracking=True,
                                       help="This is checked if the sampling is done by the customer.")
    pack_ids = fields.Many2many('lims.parameter.pack', string='Packs', readonly=True, context={'active_test': False})
    method_param_charac_ids = fields.Many2many('lims.method.parameter.characteristic', string='Parameters',
                                               readonly=True, context={'active_test': False})
    all_sop_received = fields.Boolean('All test received', compute='compute_all_sop_received', store=True,
                                      help="This is checked if the are no sops in a 'draft' or a 'plan' state.")
    assigned_to = fields.Many2one('res.users', 'Assigned to', tracking=True,
                                  help="The user at which is assign this analysis.")
    address = fields.Char('Address', tracking=True)
    sample_id = fields.Many2one('lims.analysis.request.sample')
    analysis_duration = fields.Char('Analysis duration in days (start > end)', compute='compute_analysis_duration',
                                    store=True, help='Total duration of analysis calculated from date start to date '
                                                     'end (displayed in days)')
    analysis_duration_time = fields.Float('Analysis duration in hours (start > end)',
                                          compute='compute_analysis_duration', store=True,
                                          help='Total duration of analysis calculated from date start to date end '
                                               '(displayed in hours)'
                                          )
    analysis_out_of_time = fields.Boolean('Out Of Time', compute='compute_analysis_duration', store=True,
                                          help="This will be checked if the time between the date start and "
                                               "the date done is greater than the highest duration present on the packs"
                                               " of the analysis.")
    change = fields.Boolean('Change', compute='compute_change', store=True, copy=False)
    analysis_time = fields.Float('Analysis time (reception > end)', compute='compute_analysis_time', store=True,
                                 copy=False,
                                 help='Total duration of analysis calculated from sample reception to date end')
    partner_contact_ids = fields.Many2many('res.partner', 'rel_analysis_contact', 'analysis_id', 'partner_id',
                                           string='Customer contacts',
                                           help="Contacts of the partner, sometimes used for the mail recipients.")
    date_sample_begin = fields.Datetime('Date Sample begin', help="Date of the begin of the sample.")
    reception_deviation = fields.Boolean('Reception Deviation(s)')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium (*)'), ('3', 'High (**)'), ('4', 'Highest (***)')],
                                default='1', tracking=True, help="Priority of the analysis.")
    date_validation2 = fields.Datetime(copy=False,
                                       help="This date is fulfil at the moment when the analysis switch to 'Validated 2' stage.")
    sample_condition_id = fields.Many2one('lims.sample.condition', string="Sample condition")
    comment = fields.Html('Internal note', tracking=True,
                          help="Additional comment addressed to the internal team (won't be printed on analysis report)")
    pack_of_pack_ids = fields.Many2many('lims.parameter.pack', 'analysis_id_pack_id_rel', 'analysis_id', 'pack_id',
                                        string='Pack of packs', readonly=1, context={'active_test': False})
    product_id = fields.Many2one('product.product', 'Product', domain=[('lims_for_analysis', '=', True)],
                                 help="Product of the analysis, that can be restricted by the matrix of the analysis.")

    @api.model
    def get_selection_state(self):
        return [('init', _('Init')),
                ('conform', _('Conform')),
                ('not_conform', _('Not Conform')),
                ('unconclusive', _('Inconclusive'))]

    @api.model
    def get_state_translated(self, state_to_translate=False):
        """
        Get the state translated for a analysis used in Qweb or reports.
        :return:
        """
        if state_to_translate:
            return dict(self.get_selection_state())[state_to_translate]
        return dict(self.get_selection_state())[self.state] if self.state else False

    @api.depends('matrix_id')
    def compute_regulation_id_domain_ids(self):
        method_parameter_characteristic_ids = self.env['lims.method.parameter.characteristic'].search([])
        all_regulation_ids = self.env['lims.regulation'].search([])
        for record in self:
            if record.matrix_id:
                regulation_ids = method_parameter_characteristic_ids.filtered(
                    lambda m: m.matrix_id == record.matrix_id
                ).mapped('regulation_id')
            else:
                regulation_ids = all_regulation_ids
            record.regulation_id_domain_ids = [(6, 0, regulation_ids.ids)]

    @api.depends('regulation_id')
    def compute_matrix_id_domain_ids(self):
        method_parameter_characteristic_ids = self.env['lims.method.parameter.characteristic'].search([])
        all_matrix_ids = self.env['lims.matrix'].search([])
        for record in self:
            if record.regulation_id:
                matrix_ids = method_parameter_characteristic_ids.filtered(
                    lambda m: m.regulation_id == record.regulation_id
                ).mapped('matrix_id')
            else:
                matrix_ids = all_matrix_ids
            record.matrix_id_domain_ids = [(6, 0, matrix_ids.ids)]

    def write(self, vals):
        if vals.get('sample_name') and self.mapped('sample_id') and not self.env.context.get('force_write'):
            self.mapped('sample_id').with_context(force_write=True).write({'name': vals.get('sample_name')})
        return super().write(vals)

    @api.depends('date_done', 'date_sample_receipt')
    def compute_analysis_time(self):
        for record in self.filtered(lambda a: a.date_sample_receipt and a.date_done):
            analysis_time = record.date_done - record.date_sample_receipt
            record.analysis_time = timedelta_to_hours(analysis_time)

    @api.depends('sop_ids', 'sop_ids.stage_id')
    def compute_all_sop_received(self):
        for record in self:
            record.all_sop_received = record.sop_ids and not record.sop_ids.filtered(
                lambda s: s.rel_type in ['draft', 'plan'])

    def check_accreditation_in_result(self):
        result_ids = self.get_results()
        for result_id in filter(lambda r: r.method_param_charac_id.accreditation != r.accreditation, result_ids):
            result_id.accreditation = result_id.method_param_charac_id.accreditation

    def get_result_rounded(self, value):
        digits = self.env['decimal.precision'].precision_get('Analysis Result')
        return round(value, digits)

    @api.depends('result_num_ids', 'result_num_ids.change', 'result_sel_ids', 'result_sel_ids.change', 'result_compute_ids',
                 'result_compute_ids.change', 'result_text_ids', 'result_text_ids.change')
    def compute_change(self):
        for record in self.filtered(lambda a: filter(lambda r: not r.change, a.get_results())):
            record.change = False
        for record in self.filtered(lambda a: filter(lambda r: r.change, a.get_results())):
            record.change = True

    @api.depends('date_start', 'date_done')
    def compute_analysis_duration(self):
        for record in self.filtered(lambda r: r.date_start and r.date_done):
            delta = record.date_done - record.date_start
            record.analysis_duration_time = timedelta_to_hours(delta)
            hours = f'0{int(delta.seconds / 3600)}' if int(delta.seconds / 3600) < 10 else int(delta.seconds / 3600)
            rest = (delta.seconds / 3600 - int(delta.seconds / 3600))
            mins = f'0{int(rest * 60)}' if int(rest * 60) < 10 else int(rest * 60)
            rest = rest * 60 - int(rest * 60)
            secs = f'0{int(rest * 60)}' if int(rest * 60) < 10 else int(rest * 60)
            record.analysis_duration = _('{} days, {}:{}:{}').format(delta.days, hours, mins, secs)
            if record.pack_ids:
                highest_duration = record.pack_ids.sorted(key=lambda p: p.duration, reverse=True)[0].duration
                if highest_duration * 3600 < delta.total_seconds():
                    record.analysis_out_of_time = True

    @api.onchange('laboratory_id')
    def onchange_laboratory_id(self):
        if self.laboratory_id:
            self.category_id = self.laboratory_id.default_analysis_category_id
        default_category_id = self.env.context.get('default_category_id', False)
        if default_category_id:
            self.category_id = default_category_id

    def print_container(self):
        """
        Print containers
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'print.qweb.container.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_ids': self.ids}
        }

    def print_label(self):
        """
        Print the labels
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'print.qweb.label.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_ids': self.ids}
        }

    @api.onchange('external_sampling')
    def onchange_external_sampling(self):
        """
        If the sampling come from the customer, there is no sampler in the analysis
        :return:
        """
        if self.external_sampling:
            self.sampler_id = False

    def print_report(self):
        if not self.date_report:
            self.date_report = fields.Datetime.now()
        return self.env.ref('lims_base.lims_analysis_report_action').report_action(self)

    def set_option_impression(self, report_type):
        """
            set option impression (if the user want print preview pdf/html)
        :param report_type: html or pdf
        :return:
        """
        report_id = self.env.ref('lims_base.lims_analysis_report_action')
        report_id.write({
            'report_type': report_type,
        })

    def do_print_preview_html(self):
        self.sudo().set_option_impression('qweb-html')
        return self.print_report()

    def do_print(self):
        self.sudo().set_option_impression('qweb-pdf')
        return self.print_report()

    def do_print_preview_pdf(self):
        self.sudo().set_option_impression('qweb-pdf')
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/pdf/{0}/{1}'.format(
                self.env.ref('lims_base.lims_analysis_report_action').report_name, self.id),
            'target': 'new',
        }

    def format_result(self, value, method_parameter_charac, lang=False, dec=False):
        """ Mainly used in qwebs
        :param lang: lang of the qweb partner
        :param value: the value of the result with X decimal
        :param method_parameter_charac: the method parameter charac of the result
        :return: the value of the result with nb decimal to show
        """
        value = formatLang(self.with_context(lang=lang).env, value,
                           digits=dec or method_parameter_charac.nbr_dec_showed)
        return value

    def get_value_of_result_id(self, result_id):
        """Mainly used in qwebs
        :param result_id: line of a result
        :return: dict with key: uom/method_param_charac_id/value/limit_value
        (if the field doesn't exist the value in the key = '')
        """
        result_id = result_id.sudo()
        partner_lang = result_id.analysis_id.partner_id.lang
        self = self.sudo()
        result_vals = {}
        val_formula = result_id.get_float_value()
        digits = self.env['decimal.precision'].precision_get('Analysis Result')
        standards = ','.join(standard.name for standard in result_id.method_param_charac_id.method_id.standard_ids)
        standards_parameter = ','.join(standard.name for standard in result_id.method_param_charac_id.standard_ids)
        result_vals.update({
            'analysis_id': result_id.analysis_id.name,
            'uom': result_id.uom_id.name if 'uom_id' in result_id._fields and result_id.uom_id else '',
            'rel_type': result_id.rel_type if 'rel_type' in result_id._fields else False,
            'sample_name': result_id.analysis_id.sample_name if result_id.analysis_id else '',
            'value': result_id.get_result_value(lang=partner_lang),
            'limit_state': result_id.state or '',
            'limit_message': '',
            'state': dict(result_id.with_context(lang=partner_lang).get_selection_state()).get(result_id.state),
            'method_id': result_id.method_id,
            'comment': result_id.comment if result_id.comment and result_id.show else '',
            'accreditation': result_id.accreditation,
            'accreditation_ids': result_id.accreditation_ids,
            'standard': standards,
            'standard_parameter': standards_parameter,
            'method_parameter_charac': result_id.method_param_charac_id.tech_name if
                'method_param_charac_id' in result_id._fields else '',
            'instruction': result_id.method_param_charac_id.work_instruction_id.name or
                           result_id.method_id.work_instruction_id.name or '',
        })

        if('limit_result_ids' in result_id._fields or 'limit_compute_result_ids' in result_id._fields) and \
        result_vals.get('value'):
            val, limit = self.get_limited_value(result_id, val_formula, digits)
            result_vals.update({
                'limit_value': val
            })
            if limit:
                result_vals.update({
                    'limit_state': limit.state,
                    'limit_message': limit.message
                })

        if result_vals.get('limit_state') == 'not_conform':
            result_vals['html_class'] = 'result_not_conform'
        # add values specific to certain types of results
        result_id.add_specific_values(result_vals, lang=partner_lang)
        return result_vals

    def get_limited_value(self, result_id, val_formula, digits):
        # to-do Change the aspect of this function, send only conform limits.
        val = ''
        limit = False
        decision_limit_result_id = False
        limit_ids = False
        if ('decision_limit_result_id' in result_id._fields) and result_id.decision_limit_result_id:
            decision_limit_result_id = result_id.decision_limit_result_id
        elif 'limit_result_ids' in result_id._fields:
            limit_ids = result_id.limit_result_ids.filtered(lambda l: l.type_alert == 'alert')
            if not limit_ids:
                limit_ids = result_id.limit_result_ids
        elif 'limit_compute_result_ids' in result_id._fields:
            limit_ids = result_id.limit_compute_result_ids.filtered(lambda l: l.type_alert == 'alert')
            if not limit_ids:
                limit_ids = result_id.limit_compute_result_ids
        if limit_ids or decision_limit_result_id:
            if not decision_limit_result_id:
                for limit_id in limit_ids:
                    if limit_id.operator_from == '<>':
                        operator_from = '!='
                    elif limit_id.operator_from == '=':
                        operator_from = '=='
                    else:
                        operator_from = limit_id.operator_from
                    if limit_id.operator_to:
                        if limit_id.operator_to == '<>':
                            operator_to = '!='
                        elif limit_id.operator_to == '=':
                            operator_to = '=='
                        else:
                            operator_to = limit_id.operator_to
                        formula = '%s %s %s and %s %s %s' % (
                            round(val_formula, digits), operator_from,
                            round(limit_id.limit_value_from, digits),
                            round(val_formula, digits), operator_to,
                            round(limit_id.limit_value_to, digits))
                    else:
                        formula = '%s %s %s' % (
                            round(val_formula, digits), operator_from,
                            round(limit_id.limit_value_from, digits))
                    if eval(formula):
                        limit = limit_id
                        break
            else:
                limit = decision_limit_result_id
            if limit:
                if limit.operator_from == '<=':
                    symbol_from = html5.get('le;')
                elif limit.operator_from == '>=':
                    symbol_from = html5.get('ge;')
                else:
                    symbol_from = limit.operator_from
                val = 'X ' + symbol_from + ' ' + str(limit.limit_value_from)

                if limit.operator_to:
                    if limit.operator_to == '<=':
                        symbol_to = html5.get('le;')
                    elif limit.operator_to == '>=':
                        symbol_to = html5.get('ge;')
                    else:
                        symbol_to = limit.operator_to
                    val = str(limit.limit_value_from) + ' ' + symbol_from + ' X ' + symbol_to + ' ' + str(
                        limit.limit_value_to)
        return val, limit

    def get_value(self, value, is_null, partner_lang, method_param_charac_id, corrected_loq, max_report_value=False):
        """
        Get value from value or corrected_value
        :param value: value from result
        :param is_null: is_null from result
        :param partner_lang: lang
        :param method_param_charac_id: method from result
        :param corrected_loq: corrected_loq (loq for value, corrected_loq for corrected_value)
        :param max_report_value: only for corrected_value
        :return:
        """
        val = value
        if is_null:
            val = self.format_result(0, method_param_charac_id, lang=partner_lang,
                                     dec=method_param_charac_id.nbr_dec_showed or 0)
        elif value < corrected_loq and not method_param_charac_id.not_check_loq:
            val = f' < {self.format_result(corrected_loq, method_param_charac_id, lang=partner_lang, dec=method_param_charac_id.nbr_dec_showed or 0)}'
        elif value > corrected_loq and not method_param_charac_id.not_check_loq:
            val = str(self.format_result(value, method_param_charac_id, lang=partner_lang,
                                         dec=method_param_charac_id.nbr_dec_showed or 0))
        elif value > max_report_value and not method_param_charac_id.not_check_max_value:
            if max_report_value:
                val = f' > {self.format_result(max_report_value, method_param_charac_id, lang=partner_lang, dec=method_param_charac_id.nbr_dec_showed or 0)}'
            else:
                val = f' > {self.format_result(value, method_param_charac_id, lang=partner_lang, dec=method_param_charac_id.nbr_dec_showed or 0)}'
        return val

    def get_results_from_analysis(self, option_print=False, sorted_by_method=False):
        """
        Mainly used in qwebs, give all the result for one analysis
        Sort by method (sequence, id)

        :param option_print:
        :param sorted_by_method:
        :return: list of results
        """
        cancel_rework_stage_id = self.env['lims.result.stage'].sudo().search([('type', 'in', ['cancel', 'rework'])])
        result = list(filter(lambda r: r.stage_id not in cancel_rework_stage_id, self.get_results()))
        if option_print:
            result = list(filter(lambda r: r.print_on_report, result))
        if sorted_by_method:
            result.sort(key=lambda r: (r.method_id.sequence,
                                       r.method_id.id,
                                       r.method_param_charac_id.parameter_id.sequence))
        return result

    def get_vals_for_recurrence(self):
        """
        Used in duplicate and lims_analysis_recurrence
        :return: return a dictionary with fields set as default value but except some fields
        """
        return {'active': True,
                'category_id': self.category_id.id,
                'matrix_id': self.matrix_id.id,
                'note': self.note,
                'partner_id': self.partner_id.id,
                'customer_ref': self.customer_ref,
                'state': False,
                'stage_id': self.get_default_stage(),
                'laboratory_id': self.laboratory_id.id,
                'parent_id': self.parent_id.id,
                'regulation_id': self.regulation_id.id,
                'description': self.description,
                'request_id': self.request_id.id,
                'sampler_id': self.sampler_id.id,
                'dilution_factor': self.dilution_factor,
                'date_done': False,
                'date_sample_receipt': False,
                'sample_name': False,
                'date_report': False,
                'date_start': False,
                'date_plan': False,
                'date_sample': False,
                'result_num_ids': False,
                'result_sel_ids': False,
                'result_compute_ids': False,
                'reason_id': self.reason_id.id,
                'sop_ids': False,
                'report_done': False,
                'cancel_reason': '',
                'is_duplicate': False,
                'ref_sample_id': False,
                'pack_ids': [(4, pack_id.id) for pack_id in self.pack_ids],
                'method_param_charac_ids': [(4, method_param_charac_id.id) for method_param_charac_id in
                                            self.method_param_charac_ids],
                'product_id': self.product_id.id,
                }

    @api.depends('result_num_ids', 'result_num_ids.stage_id', 'result_sel_ids', 'result_sel_ids.stage_id',
                 'result_compute_ids', 'result_compute_ids.stage_id', 'result_text_ids', 'result_text_ids.stage_id')
    def compute_is_incomplete(self):
        """
        Compute if a result is cancel, then the analysis is incomplete
        :return:
        """
        for record in self:
            is_incomplete = record.result_num_ids.filtered(lambda r: r.rel_type == 'cancel') or \
                            record.result_sel_ids.filtered(lambda r: r.rel_type == 'cancel') or \
                            record.result_compute_ids.filtered(lambda r: r.rel_type == 'cancel') or \
                            record.result_text_ids.filtered(lambda r: r.rel_type == 'cancel') or \
                            False
            if not is_incomplete:
                all_method_param_charac = record._get_all_method_param_charac()
                is_incomplete = all_method_param_charac != record.pack_ids.mapped(
                    'parameter_ids.method_param_charac_id') + record.method_param_charac_ids
            record.is_incomplete = is_incomplete

    def _get_all_method_param_charac(self):
        all_method_param_charac = self.env['lims.method.parameter.characteristic']
        all_method_param_charac += self.result_num_ids.method_param_charac_id
        all_method_param_charac += self.result_sel_ids.method_param_charac_id
        all_method_param_charac += self.result_compute_ids.method_param_charac_id
        all_method_param_charac += self.result_text_ids.method_param_charac_id
        return all_method_param_charac

    @api.depends('name', 'partner_id')
    def get_display_name_calendar(self):
        """
        compute the display name for calendar view
        :return:
        """
        for record in self:
            display_calendar = record.name
            if record.partner_id:
                display_calendar = f'{display_calendar} - {record.partner_id.name} - {record.matrix_id.name}'
            record.display_calendar = display_calendar

    def duplicate(self):
        """
        duplicate the analysis (with SOP and result)
        :return: view of the new analysis
        """
        new_analysis_ids = []
        for record in self:
            vals = record.get_vals_for_recurrence()
            vals.update({
                'is_duplicate': True,
                'parent_id': record.id,
                'due_date': False,
                'change': False,
                'date_plan': record.date_plan,
                'date_sample': record.date_sample,
            })
            new_analysis = record.copy(default=vals)
            new_analysis_ids.append(new_analysis.id)
            new_analysis.message_post(
                body=_("The analysis {0} has been duplicate from {1}.".format(new_analysis.name, record.name))
            )
        if new_analysis_ids:
            return {
                'name': _('Analysis'),
                'view_mode': 'tree,form,pivot,graph,calendar',
                'res_model': 'lims.analysis',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', new_analysis_ids)],
            }

    @api.depends('sop_ids')
    def compute_nb_sop(self):
        """
        Compute number of SOP for the analysis and compute number of SOP in request after
        :return:
        """
        for record in self:
            record.nb_sop = len(record.sop_ids)


    @api.model_create_multi
    def create(self, vals_list):
        """
        Create analysis, give the name of the analysis depends of the sequence set in laboratory
        If no sample_name is set, give the same name than the analysis
        :param vals_list:
        :return:
        """
        for vals in vals_list:
            labo = self.env['lims.laboratory'].browse(int(vals.get('laboratory_id')))
            if labo.seq_analysis_id:
                vals.update({'name': labo.seq_analysis_id.next_by_id()})
            else:
                raise exceptions.UserError(_('No sequence for the analysis in the laboratory'))
            if not vals.get('sample_name'):
                vals.update({'sample_name': vals.get('name')})
        records = super().create(vals_list)
        if request_ids := records.mapped('request_id'):
            request_ids.filtered(lambda r: r.state == 'done').write({'state': 'accepted'})
        return records

    def copy(self, default=None):
        """
        Copy the analysis if 'no_sop' is not in the context, create the sop related to the analysis
        :param default:
        :return:
        """
        self.ensure_one()
        analysis_stage_id = self.get_default_stage()
        if not analysis_stage_id:
            raise exceptions.ValidationError(_('No default analysis stage found'))
        if not default:
            default = {'stage_id': analysis_stage_id}
        else:
            default['stage_id'] = analysis_stage_id
        res = super().copy(default=default)
        res.sample_name = res.name
        if not self.env.context.get('no_sop'):
            for sop_id in self.sop_ids:
                res.sop_ids += sop_id.copy(default={'analysis_id': res.id})
        return res

    def add_parameters_wizard_action(self):
        """
        Open the wizard for add parameter in the analysis
        :return:
        """
        return {
            'name': _('Add parameters'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.parameters.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_id': self.id}
        }

    def create_sop(self):
        """
        Create SOP for this analysis
        :return:
        """
        sop_obj = self.env['lims.sop']
        vals_list = []
        for record in self:
            method_ids = record.sudo().get_method_ids()
            for method_id in method_ids:
                if sop_vals := record.sudo().get_sop_vals(method_id):
                    vals_list.append(sop_vals)
        sop_ids = sop_obj.create(vals_list)
        if self.env.context.get('to_plan_sop'):
            self.mapped('sop_ids').do_plan()
        elif self.filtered(lambda r: r.rel_type == 'plan'):
            self.filtered(lambda r: r.rel_type == 'plan').mapped('sop_ids').do_plan()
        elif self.filtered(lambda r: r.rel_type not in ['draft', 'plan']):
            records = sop_ids.filtered(lambda s: s.analysis_id.rel_type not in ['draft', 'plan'])
            records.do_plan()
            records.do_todo()

    def get_method_ids(self):
        """
        Get all method used in the analysis (for all type of result)
        :return: method_ids
        """
        self.ensure_one()
        method_ids = self.env['lims.method']

        for method_id in self.result_num_ids.method_param_charac_id.method_id:
            if method_id not in method_ids:
                method_ids += method_id
        for method_id in self.result_sel_ids.method_param_charac_id.method_id:
            if method_id not in method_ids:
                method_ids += method_id
        for method_id in self.result_compute_ids.method_param_charac_id.method_id:
            if method_id not in method_ids:
                method_ids += method_id
        for method_id in self.result_text_ids.method_param_charac_id.method_id:
            if method_id not in method_ids:
                method_ids += method_id
        return method_ids

    def get_parameter_ids(self, stage_ids=None):
        """
        Get all parameter characteristic used in the analysis (for all type of result)
        :return: method_ids
        :param stage_ids:
        :return:
        """
        self.ensure_one()
        parameter_ids = self.env['lims.method.parameter.characteristic']
        stage_to_filter = ""
        if stage_ids:
            stage_to_filter = lambda r: r.rel_type not in stage_ids
        parameter_ids += self.result_num_ids.filtered(stage_to_filter).method_param_charac_id
        parameter_ids += self.result_sel_ids.filtered(stage_to_filter).method_param_charac_id
        parameter_ids += self.result_compute_ids.filtered(stage_to_filter).method_param_charac_id
        parameter_ids += self.result_text_ids.filtered(stage_to_filter).method_param_charac_id
        return parameter_ids

    def get_analysis_packs_and_pack_of_packs(self):
        packs = self.env['lims.parameter.pack']
        for record in self.filtered(lambda a: a.rel_type != 'cancel'):
            packs += record.pack_ids + record.pack_of_pack_ids
        return packs

    def get_sop_vals(self, method_id):
        """
        Value for create sop related to an analysis
        :param method_id: lims.method
        :return:
        """
        self.ensure_one()
        sop_vals = {
            'method_id': method_id.id,
            'analysis_id': self.id,
            'result_num_ids': [(4, result_id.id) for result_id in self.result_num_ids.filtered(
                lambda r: r.method_param_charac_id.method_id == method_id and not r.sop_id)],
            'result_sel_ids': [(4, result_sel_id.id) for result_sel_id in self.result_sel_ids.filtered(
                lambda r: r.method_param_charac_id.method_id == method_id and not r.sop_id)],
            'result_text_ids': [(4, result_text_id.id) for result_text_id in self.result_text_ids.filtered(
                lambda r: r.method_param_charac_id.method_id == method_id and not r.sop_id)],
            'result_compute_ids': [(4, compute_result_id.id) for compute_result_id in self.result_compute_ids.filtered(
                lambda r: r.method_param_charac_id.method_id == method_id and not r.sop_id)],
            'labo_id': self.laboratory_id.id,
            'note': self.note,
            'due_date': self.due_date,
        }
        if sop_vals.get('result_num_ids') or sop_vals.get('result_sel_ids') or sop_vals.get('result_compute_ids') or \
                    sop_vals.get('result_text_ids'):
            return sop_vals
        return {}

    def open_analysis_sop(self):
        """
        Open view for SOP (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Test',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.sop',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'context': {'default_analysis_id': self.id,
                        'search_default_analysis_id': self.id,
                        },
        }

    def do_plan(self, plan_stage_id=False):
        """
        Pass the analysis in stage "plan", check if all sop are created if not create the missing SOP
        :return:
        """
        if not plan_stage_id:
            plan_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'plan')], limit=1)
        if plan_stage_id:
            self.write({
                'stage_id': plan_stage_id.id,
            })
            self.filtered(lambda r: len(r.sudo().get_method_ids()) > r.nb_sop).with_context(
                to_plan_sop=True).create_sop()
            self.mapped('sop_ids').filtered(lambda s: s.rel_type == 'draft').do_plan()
        else:
            raise exceptions.ValidationError(_('No stage "plan" found'))

    def do_todo(self, todo_stage_id=False):
        """
        Pass the analysis in stage "todo", Pass the request in state "WIP", Create SOP if there is not,
        Pass the SOPs in stage "todo"
        :return:
        """
        if not todo_stage_id:
            todo_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'todo')], limit=1)
        if not todo_stage_id:
            raise exceptions.ValidationError('No stage "to do" found')
        self.write({
            'stage_id': todo_stage_id.id,
        })
        self.do_todo_requests()
        for record in self:
            if len(record.get_method_ids()) > record.nb_sop:
                record.create_sop()
        self.do_todo_sops()

    def do_todo_requests(self):
        """
        Apply changes on request when analysis state change to todo
        """
        if request_ids := self.mapped('request_id'):
            request_ids.write({
                'state': 'in_progress'
            })

    def do_todo_sops(self):
        """
        Apply changed on SOP when analysis state change to todo
        """

        if sop_ids:= self.mapped('sop_ids'):
            sop_ids.filtered(lambda s: s.rel_type == 'plan').do_todo()

    def do_wip(self, wip_stage_id=False):
        """
        Pass the analysis in stage "WIP"
        :return:
        """
        if not wip_stage_id:
            wip_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'wip')], limit=1)
        if wip_stage_id:
            self.write({
                'stage_id': wip_stage_id.id,
            })
            self.filtered(lambda r: not r.date_start).write({'date_start': fields.Datetime.now()})
        else:
            raise exceptions.ValidationError('No stage "wip" found')

    def do_done(self, done_stage_id=False):
        """
        Pass the analysis in stage "Done"
        :return:
        """
        if not done_stage_id:
            done_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'done')], limit=1)
        if done_stage_id:
            self.write({
                'stage_id': done_stage_id.id,
                'date_done': fields.Datetime.now()
            })
        else:
            raise exceptions.ValidationError('No stage "done" found')

    def do_validated(self, validated_stage_id=False):
        """
        Pass the analysis in stage "Validated"
        :return:
        """
        if not validated_stage_id:
            validated_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'validated1')], limit=1)
        if validated_stage_id:
            self.write({
                'stage_id': validated_stage_id.id,
            })
        else:
            raise exceptions.ValidationError('No stage "validated1" found')

    def do_validation2(self, validated2_stage_id=False):
        """
        Pass the analysis in stage "second validation", Check if the request could pass in stage "done"
        :return:
        """
        if not validated2_stage_id:
            validated2_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'validated2')], limit=1)
        if not validated2_stage_id:
            raise exceptions.ValidationError('No stage "validated2" found')
        if self.filtered(lambda a: (a.stage_id.type != 'validated1' and not a.laboratory_id.only_second_validation)
                                       or (a.stage_id.type not in ['validated1', 'done'] and
                                           a.laboratory_id.only_second_validation)):
            raise exceptions.ValidationError(_('Only validated analysis can be set in second validation. \n'
                                               'Two-step validation can be avoided in the laboratory configuration.'))
        self.write({
            'stage_id': validated2_stage_id.id,
            'date_validation2': fields.Datetime.now(),
        })
        if request_ids := self.mapped('request_id'):
            request_ids.check_done_state()
            request_ids.compute_analysis_state()

    def do_cancel(self, cancel_reason='', cancel_stage_id=False):
        """
        Cancel the analysis, Cancel the SOPs, Compute the analysis_state in request,
        Check if the request could pass in stage "done"
        :param cancel_reason:
        :return:
        """
        if not cancel_stage_id:
            cancel_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'cancel')], limit=1)
        analysis = self.filtered(lambda r: r.stage_id != cancel_stage_id)
        if cancel_stage_id and analysis:
            analysis.write({
                'stage_id': cancel_stage_id.id,
                'cancel_reason': cancel_reason,
            })
            if sop_ids := analysis.mapped('sop_ids').filtered(lambda s: s.stage_id.type != 'cancel'):
                sop_ids.do_cancel()
            if request_ids := analysis.mapped('request_id'):
                request_ids.compute_analysis_state()
                request_ids.check_done_state()
        elif not cancel_stage_id:
            raise exceptions.ValidationError('No stage "cancel" found')

    def do_rework(self):
        """
        Pass the request in state "accepted", Pass the the current analysis in cancel,
        Pass the new analysis in stage "plan", Copy the samples, open the view on the new analysis
        :return:
        """
        self.ensure_one()
        if self.rel_type != 'cancel':
            self.do_cancel()
        if self.request_id:
            self.request_id.state = 'accepted'
        duplicated_analysis = self.copy(default={'is_duplicate': True, 'parent_id': self.id})
        duplicated_analysis.do_plan()
        if sample_id := self.env['lims.analysis.request.sample'].sudo().search([('analysis_id', '=', self.id)]):
            duplicated_sample_id = sample_id.copy()
            duplicated_sample_id.analysis_id = duplicated_analysis.id
        return {
            'name': _('Analysis'),
            'view_mode': 'tree,form,pivot,graph,calendar',
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', '=', duplicated_analysis.id)],
        }

    def check_state(self):
        """
        if all SOPs are cancel/done pass the analysis in stage "done"
        :return:
        """
        self = self.sudo()
        for record in self.filtered(lambda r: r.stage_id.type != 'cancel'):
            # if all sop are cancelled then analysis is cancelled
            if all(sop_id.stage_id.type == 'cancel' for sop_id in record.sop_ids):
                record.do_cancel()
            elif all(sop_id.stage_id.type in ['validated', 'cancel'] for sop_id in record.sop_ids):
                record.check_state_validated()
            elif all(sop_id.stage_id.type in ['done', 'validated', 'cancel'] for sop_id in record.sop_ids):
                record.do_done()

    def check_state_validated(self):
        """
        if all SOPs are cancel/validated pass the analysis in stage "validated"
        :return:
        """
        for record in self.filtered(lambda r: r.stage_id.type != 'cancel'):
            if all(sop_id.rel_type in ['validated', 'cancel'] for sop_id in record.sop_ids):
                if record.laboratory_id.only_second_validation:
                    record.do_validation2()
                else:
                    record.do_validated()

    def check_analysis_state(self):
        """
        Check the state of the analysis (conform, not conform, unconclusive) depends on the state of the results
        :return:
        """
        self = self.sudo()
        for record in self:
            record.state = record.sudo().get_sop_status()

    def get_sop_status(self):
        """
        Check the state in the results of the analysis
        :return:
        """
        self.ensure_one()
        sops = self.sop_ids.filtered(lambda s: s.rel_type != "cancel")
        if sops.filtered(lambda r: r.state == 'not_conform'):
            return 'not_conform'
        if self.laboratory_id.unconclusive_priority:
            if sops.filtered(lambda r: r.state == 'unconclusive'):
                return 'unconclusive'
            if sops.filtered(lambda r: r.state == 'conform'):
                return 'conform'
        else:
            if sops.filtered(lambda r: r.state == 'conform'):
                return 'conform'
            if sops.filtered(lambda r: r.state == 'unconclusive'):
                return 'unconclusive'
        if sops.filtered(lambda r: r.state == 'init'):
            return 'init'

    def do_cancel_wizard(self):
        return {
            'name': _('Cancel analysis'),
            'type': 'ir.actions.act_window',
            'view_form': 'form',
            'view_mode': 'form',
            'res_model': 'analysis.cancel.wizard',
            'context': {'default_analysis_ids': self.ids},
            'target': 'new',
        }

    def do_cancel_wizard_and_rework(self):
        return {
            'name': _('Cancel analysis'),
            'type': 'ir.actions.act_window',
            'view_form': 'form',
            'view_mode': 'form',
            'res_model': 'analysis.cancel.wizard',
            'context': {'default_analysis_ids': self.ids, 'do_rework': True},
            'target': 'new',
        }

    def second_validation_mass_change(self):
        return {
            'name': _('Second validation mass change'),
            'type': 'ir.actions.act_window',
            'view_form': 'form',
            'view_mode': 'form',
            'res_model': 'analysis.second.validation.mass.change.wizard',
            'context': {'default_analysis_ids': self.ids},
            'target': 'new',
        }

    def get_results(self):
        return list(self.result_num_ids) + list(self.result_sel_ids) + list(self.result_text_ids) + \
            list(self.result_compute_ids)

    def get_results_filtered(self, stage=None, domain=None):
        """
        This function is used to get all result (prefilter)
        :param stage: Must be an iterable of string
        :param domain: Must be an 'lambda' function.
        :return:
        """
        if stage:
            domain = lambda r: r.rel_type in stage
        if domain:
            return list(self.result_num_ids.filtered(domain)) + list(
                self.result_compute_ids.filtered(domain)) + list(
                self.result_sel_ids.filtered(domain)) + list(
                self.result_text_ids.filtered(domain))
        return self.get_results()

    def get_sops_filtered(self, remove_stage: list = None, domain=None):
        """
        Get sops from analyses, can get filtered sop_ids.
        Usually all stage will be taken except "cancel"
        So it become : analysis.get_sops_filtered(remove_stage=['cancel'])
        Or can directly set a specific Lambda to use : analysis.get_sops_filtered(domain=lambda s: s.state == 'conform')
        :param remove_stage:
        :param domain:
        :return:
        """
        if remove_stage:
            domain = lambda r: r.rel_type not in remove_stage
        return self.sop_ids.filtered(domain) if domain else self.sop_ids
    
    def archive_cascade(self):
        """
        Toggle active for analysis, sop and result
        :return:
        """
        sop_obj = self.env['lims.sop']
        sop_ids = sop_obj.with_context(active_test=False).search([('analysis_id', 'in', self.ids)])
        for record in self:
            record.toggle_active()
            record.with_context(active_test=False).result_num_ids.toggle_active()
            record.with_context(active_test=False).result_compute_ids.toggle_active()
            record.with_context(active_test=False).result_sel_ids.toggle_active()
            record.with_context(active_test=False).result_text_ids.toggle_active()
            ana_sop_ids = sop_ids.filtered(lambda x: x.analysis_id.id == record.id)
            for sop_id in ana_sop_ids:
                sop_id.toggle_active()
            # Nb sop doesn't update after archive / Unarchive
            record.nb_sop = len(ana_sop_ids)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and self.product_id.lims_for_analysis:
            self.matrix_id = self.product_id.matrix_id

    def _message_get_suggested_recipients(self):
        """
        Add partner and partner contact to the message sending box as suggestion
        (checkbox to send message so those partners and add them as followers)
        """
        recipients = super()._message_get_suggested_recipients()
        with contextlib.suppress(exceptions.AccessError):
            for record in self:
                if record.partner_id:
                    record._message_add_suggested_recipient(recipients, partner=record.partner_id, reason=_('Customer'))
                for partner_id in record.partner_contact_ids:
                    record._message_add_suggested_recipient(recipients, partner=partner_id, reason=_('Contact'))
        return recipients

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        res = super()._message_auto_subscribe_followers(updated_values, default_subtype_ids)
        if self.env['ir.config_parameter'].sudo().get_param('is_automatic_customer_follower'):
            if updated_values.get('partner_id'):
                res.append((updated_values.get('partner_id'), default_subtype_ids, False))
            if updated_values.get('partner_contact_ids'):
                contact_vals = updated_values.get('partner_contact_ids')
                # many2many vals can be presented on format ([6, 0, ids] or (4, id)]. We must handle both cases
                if isinstance(contact_vals[0], list):
                    contact_ids = updated_values.get('partner_contact_ids')[0][2]
                elif isinstance(contact_vals[0], tuple):
                    if len(contact_vals[0]) == 3:
                        contact_ids = contact_vals[0][2]
                    else:
                        contact_ids = [contact[1] for contact in contact_vals]
                else:
                    return res
                for contact_id in contact_ids:
                    res.append((contact_id, default_subtype_ids, False))
        return res

    def assign_analysis_to_self(self):
        records = self
        if self.env.context.get('from_tree_view'):
            records = self.filtered(lambda t: t.stage_id.type in ['draft', 'plan', 'todo'] and not t.assigned_to)
        records.assigned_to = records.env.user

    def clean_packs(self):
        """
        Remove parameters and packs from analyses if no results is related (e.g. after deleting a result)
        """
        for record in self:
            vals = {}
            all_params = [r.method_param_charac_id.id for r in record.get_results()]
            params_to_remove = record.method_param_charac_ids.filtered(lambda m: m.id not in all_params)
            if params_to_remove:
                vals.update({
                    'method_param_charac_ids': [Command.unlink(p.id) for p in params_to_remove],
                })
            packs_to_remove = []
            for pack_id in record.pack_ids:
                if not any([param.id in all_params for param in pack_id.parameter_ids.method_param_charac_id]):
                    packs_to_remove.append(pack_id.id)
            if packs_to_remove:
                vals.update({
                    'pack_ids': [Command.unlink(p) for p in packs_to_remove]
                })
            if vals:
                record.write(vals)

    @api.model
    def add_parameters_and_packs(self, pack_ids, param_ids):
        """
        Main function to add parameter or pack on analysis.

        :param pack_ids:
        :param param_ids:
        :return:
        """
        self.ensure_one()
        if not self.get_regulation():
            self.set_regulation(pack_ids, param_ids)
        new_packs, new_parameters = self._filter_parameters_and_packs_to_add(pack_ids, param_ids)
        parameters = self._get_method_parameter_characteristic(new_packs, new_parameters)
        result_vals_list = self._prepare_results_vals_lists(parameters)
        results_list = self._prepare_and_create_results(result_vals_list)
        self.create_sop()
        self._setup_new_results(results_list)
        # Auto-calculation when add a calculated result in WIP's stage Analysis
        if self.rel_type == 'wip' and results_list:
            computes = [type_list for type_list in results_list if type_list._name == 'lims.analysis.compute.result']
            for compute in computes:
                compute.check_computed_result(compute_result=compute)
        return new_packs, new_parameters

    @api.model
    def _filter_parameters_and_packs_to_add(self, packs, parameters):
        """
        Add possible pack of packs, packs and parameters, return the new one to create results.
        :param packs:
        :param parameters:
        :return:
        """

        packs = packs or self.env['lims.parameter.pack']
        new_packs = self.env['lims.parameter.pack']
        parameters = parameters or self.env['lims.method.parameter.characteristic']
        new_parameters = self.env['lims.method.parameter.characteristic']
        pack_of_packs = packs and packs.filtered(lambda p: p.is_pack_of_pack and p.state == 'validated' and
                                                 p.id not in self.pack_of_pack_ids.ids)
        regulation_ids = self.get_regulation()
        list_pack_of_packs = pack_of_packs and list(pack_of_packs)
        if list_pack_of_packs:
            for pack_of_pack in list_pack_of_packs:
                for p in pack_of_pack.pack_of_pack_ids:
                    if (not p.pack_id.is_pack_of_pack and p.rel_state == 'validated' and
                            p.pack_id.id not in packs.ids and p.pack_id.id not in self.pack_ids.ids):
                        packs += p.pack_id
                    else:
                        pack_of_packs += p.pack_id
                        list_pack_of_packs.append(p.pack_id)
        del list_pack_of_packs
        for pack in packs.filtered(
                lambda p: p.state == 'validated' and
                          p.id not in self.pack_ids.ids and
                          p.matrix_id.id == self.matrix_id.id and p.regulation_id.id in regulation_ids):
            new_packs += pack
        for parameter in parameters.filtered(
                lambda p: p.state == 'validated' and
                          p.id not in self.method_param_charac_ids.ids and
                          p.matrix_id.id == self.matrix_id.id and p.regulation_id.id in regulation_ids):
            new_parameters += parameter
        self.pack_ids += new_packs.filtered(lambda p: not p.is_pack_of_pack)
        self.pack_of_pack_ids += pack_of_packs
        self.method_param_charac_ids += new_parameters
        return new_packs, new_parameters

    @api.model
    def _get_method_parameter_characteristic(self, new_packs, new_parameters, dictonnary=False):
        """
        Get all parameter_characteritsics from packs to add into analysis.
        :param dictonnary:
        :param new_packs:
        :param new_parameters:
        :return:
        """
        if not dictonnary:
            dictonnary = {}
        present_ids = self._get_all_method_param_charac_id_from_analysis()
        for pack in new_packs.filtered(lambda p: not p.is_pack_of_pack):
            for pack_line in pack.parameter_ids.filtered(
                    lambda p: p.method_param_charac_id.id not in present_ids and
                                                                p.method_param_charac_id.state == 'validated'):
                dictonnary[pack_line.method_param_charac_id.id] = {'parameter': pack_line.method_param_charac_id,
                                                                   'pack': pack}
        for parameter in new_parameters.filtered(lambda p: p.id not in present_ids and not dictonnary.get(p.id)):
            dictonnary[parameter.id] = {'parameter': parameter}
        dictonnary = self._get_conditional_parameters(dictonnary, present_ids)
        return dictonnary

    @api.model
    def _get_conditional_parameters(self, dictonnary, present_ids=False):
        """
        Scan all parameters, and add all parameter defined in conditionals parameters. (Recursive !)
        :param dictonnary:
        :param present_ids:
        :return:
        """
        if not present_ids:
            present_ids = []
        conditionals = list(filter(lambda p: p.get('parameter').conditional_parameters_ids, dictonnary.values()))
        for conditional in conditionals:
            for conditional_line in conditional.get('parameter').conditional_parameters_ids.filtered(
                    lambda p: p.state == 'validated' and p.id not in present_ids and
                              p.matrix_id.id == conditional.get('parameter').matrix_id.id and
                              p.regulation_id.id == conditional.get('parameter').regulation_id.id):
                if conditional_line.id not in dictonnary:
                    dictonnary[conditional_line.id] = {'parameter': conditional_line}
                    conditionals.append({'parameter': conditional_line})
        return dictonnary

    @api.model
    def _prepare_results_vals_lists(self, parameters_dictonnary, vals_list=False):
        """
        Function build to add pack and parameter on analysis.
        Use a format-key dictonnary to use create_multi.
        See _prepare_and_create_results
        :param parameters_dictonnary:
        :param vals_list:
        :return:
        """
        if not vals_list:
            vals_list = {'nu': [], 'se': [], 'ca': [],  'tx': []}
        draft_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'draft')], limit=1)
        for parameter in parameters_dictonnary.values():
            vals = {
                    'analysis_id': self.id,
                    'method_param_charac_id': parameter['parameter'].id,
                    'pack_id': parameter['pack'].id if parameter.get('pack') else False
                }
            if sop_id := self.sop_ids.filtered(
                    lambda s: s.method_id == parameter['parameter'].method_id and s.rel_type != 'cancel'):
                vals['sop_id'] = sop_id.id
            elif not sop_id or sop_id.rel_type == 'draft':
                vals['stage_id'] = draft_stage_id.id
            vals_list[parameter['parameter'].format].append(vals)
        return vals_list

    @api.model
    def _prepare_and_create_results(self, vals_list, result_list=False):
        """
        Form a dictonnary, create results in batch, limited by parameter format.
        :param result_list:
        :param vals_list:
        :return:
        """
        if not result_list:
            results_list = []
        if vals_list['nu']:
            results_list.append(self._create_results('lims.analysis.numeric.result', vals_list, 'nu'))
        if vals_list['se']:
            results_list.append(self._create_results('lims.analysis.sel.result', vals_list, 'se'))
        if vals_list['ca']:
            results_list.append(self._create_results('lims.analysis.compute.result', vals_list, 'ca'))
        if vals_list['tx']:
            results_list.append(self._create_results('lims.analysis.text.result', vals_list, 'tx'))
        return results_list

    def _create_results(self, results_model, vals_list, results_type):
        """
        Private method to manage creation of result, avoid duplicate code
        :param results_model:
        :param vals_list:
        :param results_type:
        :return:
        """
        result_ids = self.env[results_model].sudo()
        return result_ids.create(vals_list[results_type])

    @api.model
    def _get_all_method_param_charac_id_from_analysis(self):
        """
        Extend the function 'get_results_from_analysis' to get all method_param_charac_id assigned to this analysis.
        :return:
        """
        return [r.method_param_charac_id.id for r in self.get_results_from_analysis()]

    @api.model
    def _setup_new_results(self, all_results):
        """
        aligns the status of a result with the status of its test.
        Sop state : plan, new result's status -> plan
        Sop state : not in draft or plan, new result's status -> todo; and for this case change sop status for sop
                    if the sop isn't in state 'todo', set to the state todo.
        :param all_results:
        :return:
        """
        for type_results in all_results:
            type_results = type_results.filtered(lambda r: r.sop_id.rel_type != 'draft')
            sops = self.env['lims.sop']
            # Apply the state of result (when created)
            type_results.filtered(lambda r: r.sop_id.rel_type == 'plan').do_plan()
            type_results.filtered(lambda r: r.sop_id.rel_type != 'plan').do_todo()
            # Change the state of test if a result is added in a test already wip, done, validated
            # -> and reset the test state to todo
            for result in type_results.filtered(lambda r: r.sop_id.rel_type in ['wip', 'done', 'validated']):
                sops += result.sop_id
            if sops:
                sops.do_todo()
            if self.stage_id.type in ['done', 'validated1', 'validated2']:
                self.do_wip()
        return all_results

    def get_regulation(self):
        return self.regulation_id.ids

    def set_regulation(self, pack_ids=None, param_ids=None):
        packs = pack_ids and pack_ids.filtered(
            lambda p: p.state == 'validated' and p.matrix_id == self.matrix_id and p.regulation_id)
        parameters = param_ids and param_ids.filtered(
            lambda p: p.state == 'validated' and p.matrix_id == self.matrix_id and p.regulation_id)
        for record in self.filtered(lambda a: not a.get_regulation()):
            regulation_id = False
            if packs:
                regulation_id = pack_ids[0].regulation_id
            elif parameters:
                regulation_id = parameters[0].regulation_id
            record.regulation_id = regulation_id


    def _compute_access_url(self):
        super()._compute_access_url()
        for analysis in self:
            analysis.access_url = f'/my/analyses/{analysis.id}'

    def get_comment(self):
        self.ensure_one()
        return self.comment if bool(html2plaintext(self.comment)) else False

    def get_parameters(self):
        self.ensure_one()
        return self.result_num_ids.method_param_charac_id + self.result_compute_ids.method_param_charac_id + \
            self.result_sel_ids.method_param_charac_id + self.result_text_ids.method_param_charac_id
