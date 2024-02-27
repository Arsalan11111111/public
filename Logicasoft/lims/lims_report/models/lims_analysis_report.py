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
from odoo import fields, models, api, tools, _, exceptions
from odoo.tools import html2plaintext
from odoo.tools.misc import formatLang
from html.entities import html5
import math

from odoo.addons.lims_base.models.res_config import check_identity_lgk


class LimsAnalysisReport(models.Model):
    _name = 'lims.analysis.report'
    _description = 'Report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def domain_report_signatory(self):
        group_validate_report_id = self.sudo().env.ref('lims_report.group_lims_validate_report')
        return [('id', 'in', group_validate_report_id.users.ids)]

    name = fields.Char('Name', required=True, help="The name of the report can be printed on reports.")
    analysis_request_id = fields.Many2one('lims.analysis.request', string='Analysis Request', tracking=True,
                                          help="This is the analysis request of the analysis involved in the report. "
                                               "If you change it, this will change the version of the report to "
                                               "the number of reports where the request is present. "
                                               "The 'Date Report Sent' of the request will be fulfilled to "
                                               "the date you send the report, and if the request was in 'Done' state, "
                                               "it will switched to the 'Report' state.")
    comment = fields.Html('External comment',
                          help='Additional comment addressed to the customer (will be printed on analysis report)')
    customer_ref = fields.Char('Ref. Customer', tracking=True,
                               help="This is initially the 'Customer Ref.' of the analysis.")
    date_sent = fields.Datetime('Date Sent', tracking=True,
                                help="If the report was validated, this date will be fulfilled on the moment the report"
                                     " is sent.")
    image_01 = fields.Binary('Image 01', help="This image is displayed in many reports, such as the 'Test report'.")
    text_image_01 = fields.Char('Text Image 01', help="This text is shown under the Image 01' on reports.")
    image_02 = fields.Binary('Image 02', help="This image is displayed in many reports, such as the 'Test report'.")
    text_image_02 = fields.Char('Text Image 02', help="This text is shown under the Image 02' on reports.")
    image_03 = fields.Binary('Image 03', help="This image is displayed in many reports, such as the 'Test report'.")
    text_image_03 = fields.Char('Text Image 03', help="This text is shown under the Image 03' on reports.")
    image_medium_01 = fields.Binary('Image Medium 01', compute="get_image_medium_01",
                                    help="This is the 'Image 01' that has been resized to a medium image.")
    image_medium_02 = fields.Binary('Image Medium 02', compute="get_image_medium_02",
                                    help="This is the 'Image 02' that has been resized to a medium image.")
    image_medium_03 = fields.Binary('Image Medium 03', compute="get_image_medium_03",
                                    help="This is the 'Image 03' that has been resized to a medium image.")
    note = fields.Html('Internal note', help="Additional comment addressed to the internal team "
                                             "(won't be printed on analysis report)")
    partner_id = fields.Many2one('res.partner', 'Customer', tracking=True,
                                 help="The client of the report, which is initially the client of the analysis. "
                                      "The lang used in the report if oftenly comes from him.")
    partner_contact_ids = fields.Many2many('res.partner', string='Contacts')
    remark = fields.Html('Remark',
                         help="If the checkbox 'Print Remark' is checked, this remark will be printed in the reports.")
    report_analysis_line_ids = fields.One2many('lims.analysis.report.line', 'report_id', string='Analysis(es)',
                                               tracking=True, help="The list of analysis involved in the report.")
    report_date = fields.Datetime('Report Date', default=lambda x: fields.Datetime.now(), tracking=True)
    signatory_01 = fields.Many2one('res.users', string='Signatory 01', domain=domain_report_signatory, tracking=True,
                                   help="The signatory can be printed on the report. If you change the laboratory,  "
                                        "the signatory will be the one present in the laboratory. "
                                        "This field has limited values to the users present in the group named "
                                        "'Allow Lims Report Validation'.")
    signatory_02 = fields.Many2one('res.users', string='Signatory 02', domain=domain_report_signatory, tracking=True,
                                   help="The signatory can be printed on the report. If you change the laboratory,  "
                                        "the signatory will be the one present in the laboratory. "
                                        "This field has limited values to the users present in the group named "
                                        "'Allow Lims Report Validation'.")
    state = fields.Selection('get_state_selection', 'State', default='draft', tracking=True)
    message_main_attachment_id = fields.Many2one(tracking=True)
    title = fields.Char('Title', tracking=True, translate=True,
                        help="The title of the report can be printed on reports.")
    version = fields.Integer('Version', default=1)
    analysis_count = fields.Integer(compute='get_analysis_count', string='Analysis Count')
    analysis_ids = fields.Many2many('lims.analysis', compute='get_analysis_count')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', tracking=True)
    previous_analysis_report_id = fields.Many2one('lims.analysis.report', 'Replace Report', tracking=True,
                                                  help="This is the report that was previously done for that analysis "
                                                       "and is now cancelled.")
    report_id = fields.Many2one('ir.actions.report', 'Report', domain=[('model', '=', 'lims.analysis.report')]
                                , tracking=True)
    report_template_id = fields.Many2one('lims.analysis.report.template', 'Report template', tracking=True)
    validator_id = fields.Many2one('res.users', 'Validator', tracking=True,
                                   help='Automatically fills in with the name of the person who validates the report.')
    tag_ids = fields.Many2many('lims.analysis.report.tag', string='Tags')
    kanban_state = fields.Selection([
        ('normal', 'Draft'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', tracking=True)
    is_locked = fields.Boolean(help="Analysis report is locked, according to laboratory configuration "
                                    "(apply to sent and/or validated stages)")
    is_classic_report = fields.Boolean("Classic report", compute='get_classic_report')

    # List of options on report
    # Options must begin with the name 'option_' and be a boolean, to be used in report models.
    option_print_comment = fields.Boolean('Print Comment', default=True, tracking=True,
                                          help="If checked, the comment of this report will be printed.")
    option_print_remark = fields.Boolean('Print Remark', default=True, tracking=True,
                                         help="If checked, the remark of this report will be printed.")
    option_print_instruction = fields.Boolean('Print Work Instruction', default=True, tracking=True,
                                              help="If checked, the work instruction of the parameter of the "
                                                   "analysis result (or of his method if empty) will be printed.")
    option_print_u = fields.Boolean('Print Uncertainty', default=True, tracking=True,
                                    help="If checked, the 'U' of the parameter of the analysis result will be printed.")
    option_print_loq = fields.Boolean('Print LOQ', default=True, tracking=True,
                                      help="If checked, the 'LOQ' of the parameter of the analysis result will be "
                                           "printed.")
    option_print_lod = fields.Boolean('Print LOD', default=True, tracking=True,
                                      help="If checked, the 'LOD' of the parameter of the analysis result will be "
                                           "printed.")
    option_print_report_limit_value = fields.Boolean('Print Report Limit Value', default=True, tracking=True,
                                                     help="If checked, the 'Limit value' of the analysis result will be"
                                                          " printed.")
    option_print_state = fields.Boolean('Print State', default=True, tracking=True,
                                        help="If checked, the 'State of conformity' of the analysis result will be "
                                             "printed.")
    option_print_conclusion = fields.Boolean('Print Conclusion', default=True, tracking=True,
                                             help="If checked, a conclusion for the analysis about his conformity state"
                                                  " and the standard prescribed by his legislation will be printed.")
    option_print_comment_result = fields.Boolean('Print Comment Result', default=True, tracking=True,
                                                 help="If checked, comments on results will be printed.")
    option_print_standard_method = fields.Boolean('Print Standard Method', default=False, tracking=True,
                                                  help="If checked, the 'Standards' of the parameter's method of "
                                                       "the analysis result will be printed.")
    option_print_standard_parameter = fields.Boolean('Print Standard Parameter', default=True, tracking=True,
                                                     help="If checked, the 'Standards' of the parameter of "
                                                          "the analysis result will be printed.")
    option_print_comment_method = fields.Boolean('Print Comment Method', default=True, tracking=True,
                                                 help="If checked, the comment of the test and alternatively "
                                                      "of the method of the analysis result will be printed.")
    option_print_general_information = fields.Boolean('Print General Information', default=True, tracking=True,
                                                      help='The general information is defined in the note field '
                                                           'of the laboratory configuration.')
    option_print_sop_id_comment = fields.Boolean('Print Test\'s Comment\'s', default=True, tracking=True,
                                                 help="If checked, the comment of the test (only) of the analysis "
                                                      "result will be printed.")

    @api.onchange('previous_analysis_report_id')
    def _onchange_previous_analysis_report_id(self):
        if self.previous_analysis_report_id:
            self.comment = self.laboratory_id.note_report_replaced

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('laboratory_id'):
                laboratory_id = self.env['lims.laboratory'].browse(int(vals.get('laboratory_id')))
                vals.update({
                    'signatory_01': laboratory_id.report_signatory_1_id.id,
                    'signatory_02': laboratory_id.report_signatory_2_id.id,
                })
        res = super().create(vals_list)
        for vals in vals_list:
            if 'state' in vals:
                res.check_lock_analysis_state_report(vals['state'])

        return res

    @api.onchange('laboratory_id')
    def onchange_laboratory_id(self):
        if self.laboratory_id:
            self.signatory_01 = self.laboratory_id.report_signatory_1_id
            self.signatory_02 = self.laboratory_id.report_signatory_2_id

    @api.onchange('report_template_id')
    def onchange_report_template_id(self):
        template_id = self.report_template_id
        if template_id:
            option_dict = template_id.get_dict_for_selected_options(template_id.option_ids)
            option_dict.update({
                'report_id': template_id.report_id.id
            })
            self.update(option_dict)

    def format_result(self, value, method_parameter_charac, lang=False):
        """ Mainly used in qwebs
        :param lang: lang of the qweb partner
        :param value: the value of the result with X decimal
        :param method_parameter_charac: the method parameter charac of the result
        :return: the value of the result with nb decimal to show
        """
        value = formatLang(self.with_context(lang=lang).env, value, digits=method_parameter_charac.nbr_dec_showed)
        return value

    def get_result_vals(self, analysis, parameter_print):
        """
        Get the information of the result, work on it and set the info in a dictionary
        :param analysis: lims.analysis
        :param parameter_print: lims.parameter.print
        :return: dictionary
        """
        results = self.get_all_result(analysis)
        partner_lang = analysis.partner_id.lang
        for result in results.filtered(lambda r: r.method_param_charac_id
                                                 and r.rel_parameter_print
                                                 and parameter_print in r.rel_parameter_print):
            result_vals = {}
            result_vals['parameter'] = result.rel_parameter_print.print_name or \
                                       result.rel_parameter_print.name
            if 'operator' in result._fields:
                symbol = ''
                if result.operator and result.operator == '<=':
                    symbol = html5.unescape('&le;')
                elif result.operator and result.operator == '>=':
                    symbol = html5.unescape('&ge;')

                if not symbol and result.operator:
                    result_vals['operator'] = result.operator if result.operator != 'range' else ''
                else:
                    result_vals['operator'] = symbol
            else:
                result_vals['operator'] = ''

            val = ''
            if 'value_id' in result._fields:
                val = result.value_id.name
            elif 'corrected_value' in result._fields:
                if parameter_print.not_check_loq or (
                        not parameter_print.not_check_loq and result.corrected_value > result.loq):
                    val = self.format_result(result.corrected_value, result.method_param_charac_id, lang=partner_lang)
                else:
                    val = result.loq
                    if result.corrected_value < result.loq:
                        val = '<' + str(val)
            elif 'value' in result._fields:
                if parameter_print.not_check_loq or (not parameter_print.not_check_loq and result.value > result.loq):
                    val = self.format_result(result.value, result.method_param_charac_id, lang=partner_lang)
                else:
                    val = result.loq
                    if result.value < result.loq:
                        val = '<' + str(val)
            result_vals['value'] = val

            val = ''
            if 'limit_value' in result._fields:
                val = self.format_result(result.limit_value, result.method_param_charac_id, lang=partner_lang)
                if result.method_param_charac_id.report_limit_value:
                    val = result.method_param_charac_id.with_context(lang=partner_lang).report_limit_value
                    result_vals['operator'] = ''
                if result.method_param_charac_id.format in ['se', 'in']:
                    val = ''
                if result.method_param_charac_id.operator == 'range':
                    uom = result.method_param_charac_id.uom.name if result.method_param_charac_id.uom else ''
                    op_from = self.format_result(result.limit_value_to, result.method_param_charac_id,
                                                 lang=partner_lang) + ' ' + uom + ' '
                    symbol = html5.unescape('&le;')
                    op_to = symbol if str(result.method_param_charac_id.operator_to) == '>=' else '<'
                    op_to += ' ' + self.format_result(result.limit_value_from, result.method_param_charac_id,
                                                      lang=partner_lang) + ' ' + uom
                    symbol = html5.unescape('&le;')
                    op_from += symbol if str(result.method_param_charac_id.operator_from) == '<=' else '<'
                    val = op_from + ' X ' + op_to
            result_vals['limit_value'] = val

            result_vals['uom'] = result.method_param_charac_id.uom.name if result.method_param_charac_id.uom else ''
            result_vals['sop_id'] = result.sop_id.comment if result.sop_id else False

            val = ''
            if result.state and result.state == 'conform':
                val = 'PASS'
            elif result.state:
                val = 'FAIL'
            result_vals['result'] = val
            result_vals['show'] = result.show if 'show' in result._fields else True

            return result_vals
        return False

    def get_analysis_list(self, page_number):
        res = self.report_analysis_line_ids.mapped('analysis_id')
        max_columns = self.option_print_standard_method and 2 or 4
        return res[page_number * max_columns - max_columns: page_number * max_columns]

    def get_page_number(self):
        max_columns = self.option_print_standard_method and 2 or 4
        return int(math.ceil(len(self.report_analysis_line_ids) / float(max_columns)))

    def get_parameter_print_group(self, page_number):
        """
        Get all the parameter_print_group necessary for print the report
        :param page_number:
        :return: dictionary of parameter.print.group
        """
        analysis_ids = self.get_analysis_list(page_number)
        all_results = []
        print_group = []
        for analysis_id in analysis_ids:
            all_results += self.get_all_result(analysis_id)
        for result in all_results:
            print_group_title_ids = result.rel_parameter_print.print_group_ids
            for print_group_title in print_group_title_ids:
                if print_group_title and print_group_title not in print_group:
                    print_group += print_group_title
        return_print_group = []
        for group in sorted(print_group, key=lambda x: x.sequence):
            if group not in return_print_group:
                return_print_group += group
        return return_print_group

    def get_all_result(self, analysis_id):
        cancel_stage_id = self.env['lims.result.stage'].search([('type', '=', 'cancel')], limit=1)
        rework_stage_id = self.env['lims.result.stage'].search([('type', '=', 'rework')], limit=1)
        result = self.env['lims.analysis.result']
        result += analysis_id.mapped('result_num_ids').filtered(
            lambda r: r.stage_id != rework_stage_id and r.stage_id != cancel_stage_id) or ''
        result += analysis_id.mapped('result_sel_ids').filtered(
            lambda r: r.stage_id != rework_stage_id and r.stage_id != cancel_stage_id) or ''
        result += analysis_id.mapped('result_compute_ids').filtered(
            lambda r: r.stage_id != rework_stage_id and r.stage_id != cancel_stage_id) or ''
        return result

    @api.onchange('analysis_request_id')
    def onchange_analysis_request_id(self):
        """
        Set the version of the report ( = nb report for one request)
        :return:
        """
        if self.analysis_request_id:
            self.version = self.analysis_request_id.nb_reports

    def print_report(self):
        """
        Print the report
        :return:
        """
        if self.report_id:
            return self.report_id.report_action(self)

    def set_option_impression(self, report_type):
        """
        Set option of impression (pdf or html)
        :param report_type:
        :return:
        """
        if self.report_id:
            self.report_id.write({
                'report_type': report_type,
            })

    def do_print_preview_pdf(self):
        """
        Open a window and show the report
        :return:
        """
        self = self.sudo()
        if self.report_id:
            self.sudo().set_option_impression('qweb-pdf')
            self.print_report()
            return {
                'type': 'ir.actions.act_url',
                'url': '/report/pdf/{0}/{1}?{2}'.format(self.report_id.report_name,
                                                        self.id,
                                                        'context={"previsualisation_mode": 1}'
                                                        ),
                'target': 'new',
            }

    def do_print_preview_html(self):
        """
        Print the report in html
        :return:
        """
        self.sudo().set_option_impression('qweb-html')
        return self.print_report()

    def do_print(self):
        """
        Print the report in pdf
        :return:
        """
        self.sudo().set_option_impression('qweb-pdf')
        return self.print_report()

    def do_print_and_send(self):
        self.report_send()
        return self.do_print()

    def get_state_selection(self):
        """
        Return all state possible
        :return:
        """
        return [
            ('draft', _('Draft')),
            ('validated', _('Validated')),
            ('sent', _('Sent')),
            ('cancel', _('Cancelled')),
        ]

    def get_analysis_count(self):
        """
        Set the number of analysis for one record
        :return:
        """
        for record in self:
            record.analysis_count = len(record.report_analysis_line_ids)
            record.analysis_ids = record.report_analysis_line_ids.analysis_id

    def open_analysis(self):
        """
        Open the analysis view
        :return:
        """
        self.ensure_one()
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('id', 'in', self.report_analysis_line_ids.mapped('analysis_id').ids)],
        }

    def report_send(self):
        if self.analysis_request_id:
            request_vals = {
                'date_report_sent': fields.Date.today()
            }
            if self.analysis_request_id.state == 'done' and self.state in ['validated', 'sent']:
                request_vals.update({
                    'state': 'report',
                })
            self.analysis_request_id.write(request_vals)
        if self.state == 'validated':
            self.write({
                'state': 'sent',
                'date_sent': fields.Datetime.now()
            })
            self.report_analysis_line_ids.mapped('analysis_id').with_context(force_write=True).write(
                {'date_report_sent': fields.Datetime.now()})
        return True

    def _analysis_report_send(self, template):
        self.ensure_one()
        partner_ids = self.get_report_automatic_followers()
        if partner_ids:
            self.with_context(force_write=True).message_subscribe(partner_ids)
        template = self.env.ref(template, False)
        if self.report_id and template and template.report_template:
            template.report_template = self.report_id
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        list_partner_ids = []
        if self.message_follower_ids:
            list_partner_ids = [f.partner_id.id for f in self.message_follower_ids]
        if self.partner_id:
            list_partner_ids.append(self.partner_id.id)
        ctx = dict(
            default_model='lims.analysis.report',
            default_res_id=self.id,
            default_partner_ids=list_partner_ids,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_write=True,
            force_email=True,
        )
        self.message_main_attachment_id = False

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def analysis_report_draft_send(self):
        return self._analysis_report_send(template='lims_report.lims_email_template_analysis_draft_report')

    def analysis_report_send(self, template=False):
        """
        There are two actions to send one open the mail composer (only for one record) and user can change mail.template
        Or an action on report's list, but user can't change the mail.template.
        :param template:
        :return:
        """
        if not template:
            template = 'lims_report.lims_email_template_analysis_report'
        if self.env.context.get('do_mass_send'):
            report_ids = self.filtered(lambda r: r.state == 'validated')
            if report_ids:
                return report_ids._mass_analysis_report_send(template=template)
            else:
                raise exceptions.ValidationError(_("There isn't a validated report in selection. Nothing to send."))
        return self._analysis_report_send(template=template)

    def get_image_medium_01(self):
        """
        Resize the picture 1
        :return:
        """
        for report in self:
            report.image_medium_01 = tools.image_resize_image_medium(report.image_01)
        return True

    def get_image_medium_02(self):
        """
        Resize the picture 2
        :return:
        """
        for report in self:
            report.image_medium_02 = tools.image_resize_image_medium(report.image_02)
        return True

    def get_image_medium_03(self):
        """
        Resize the picture 3
        :return:
        """
        for report in self:
            report.image_medium_03 = tools.image_resize_image_medium(report.image_03)
        return True

    @check_identity_lgk
    def do_validated(self):
        """
        Set the state "validated"
        :return:
        """

        if len(set(self.mapped('report_analysis_line_ids.analysis_id.stage_id.type') + ['validated2', 'cancel'])) == 2:
            self.write({
                'state': 'validated',
                'validator_id': self.env.uid,
            })
            self.mapped('report_analysis_line_ids').mapped('analysis_id').write({
                'date_report': fields.Datetime.now()
            })
        else:
            raise exceptions.ValidationError(_(
                'You can not validate report only if all analysis are in second validation or cancelled'))

    def open_cancel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_report_id': self.id}
        }

    def do_cancelled(self, reason=_('Automatic cancellation')):
        """
        Set the state "cancel"
        :return:
        """
        self.write({
            'state': 'cancel',
        })
        for record in self:
            record.message_post(body=_('Report cancelled reason: {} by {}').format(reason, self.env.user.name))

    def get_report_automatic_followers(self):
        """
        Get the partners that have to be added as followers of report (for mail sending and possibly portal)
        Separated method to ease override for customers who don't want automatic following (or another logic)
        :return: list of ids
        """
        self.ensure_one()
        analysis_contact_ids = self.report_analysis_line_ids.mapped('analysis_id').mapped('partner_contact_ids')
        return self.partner_id.ids + analysis_contact_ids.ids

    def check_lock_analysis_state_report(self, state):
        for record in self:
            if record.laboratory_id:
                lock_analysis_state_report = record.laboratory_id.lock_analysis_state_report

                lock_analysis_state_report_domain = [lock_analysis_state_report]
                if lock_analysis_state_report == 'draft':
                    lock_analysis_state_report_domain.append('validated')
                    lock_analysis_state_report_domain.append('sent')
                elif lock_analysis_state_report == 'validated':
                    lock_analysis_state_report_domain.append('sent')

                analysis_ids = record.mapped('report_analysis_line_ids.analysis_id')

                if state in lock_analysis_state_report_domain:
                    if state != 'draft':
                        record.is_locked = True
                    analysis_ids.filtered(lambda a: not a.is_locked).write({'is_locked': True})
                else:
                    record.is_locked = False
                    analysis_ids.filtered(lambda a: a.is_locked).write({'is_locked': False})

    def write(self, vals):
        if 'state' in vals:
            self.check_lock_analysis_state_report(vals['state'])
        return super(LimsAnalysisReport, self).write(vals)

    def get_classic_report(self):
        for record in self:
            if record.report_id and record.report_id.report_name == "lims_report.analysis_report_qweb":
                record.is_classic_report = True
            else:
                record.is_classic_report = False

    def _message_get_suggested_recipients(self):
        """
        Add partner and partner contact to the message sending box as suggestion
        (checkbox to send message so those partners and add them as followers)
        """
        recipients = super(LimsAnalysisReport, self)._message_get_suggested_recipients()
        try:
            for record in self:
                if record.partner_id:
                    record._message_add_suggested_recipient(recipients, partner=record.partner_id, reason=_('Customer'))
                for partner_id in record.partner_contact_ids:
                    record._message_add_suggested_recipient(recipients, partner=partner_id, reason=_('Contact'))
        except exceptions.AccessError:
            pass  # no read access rights -> just ignore suggested recipients because this implies modifying followers
        return recipients

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        res = super(LimsAnalysisReport, self)._message_auto_subscribe_followers(updated_values, default_subtype_ids)
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

    def _mass_analysis_report_send(self, template):
        """
        Enable mass sending of the Lims report
        :param template: mail template of the report
        :return: None
        """
        template = self.env.ref(template, False)
        if template:
            for record in self:
                record.message_main_attachment_id = False
                record.message_post_with_template(template.id)

    def _compute_access_url(self):
        super()._compute_access_url()
        for report in self:
            report.access_url = f'/my/reports/{report.id}'

    def get_remark(self):
        self.ensure_one()
        return self.remark if bool(html2plaintext(self.remark)) else False

    def _get_report_base_filename(self):
        self.ensure_one()
        return f'Report {self.name}'
