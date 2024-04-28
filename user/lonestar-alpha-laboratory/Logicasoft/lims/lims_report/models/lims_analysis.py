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
from odoo.exceptions import UserError
from odoo.tools import html2plaintext


# List of vals that can be written on locked analyses
ALLOWED_VALS = ['message_follower_ids', 'date_report', 'is_locked', 'sale_order_id', 'access_token']


def timedelta_to_hours(time_to_convert):
    day = time_to_convert.days
    seconds = time_to_convert.seconds
    return day * 24 + seconds / 3600


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    is_locked = fields.Boolean('Is Locked', readonly=True, copy=False, tracking=True,
                               help='Is blocked by the presence of a report for this analysis. The report state from '
                                    'which the analysis is blocked is configured in the laboratory')
    date_report_sent = fields.Datetime('Date Report Sent', copy=False,
                                       help='The date is filled with the date of the report with the most recent '
                                            'status sent.')
    nb_reports = fields.Integer(compute='compute_nb_reports', string='Reports')
    time_to_report = fields.Float(compute='compute_time_to_report', copy=False,
                                  help='Calculation of the time between the date of receipt of the sample and '
                                       'the date of sending the sample report.')

    def compute_time_to_report(self):
        for record in self:
            if record.date_report_sent and record.date_sample_receipt:
                time_to_report = record.date_report_sent - record.date_sample_receipt
                record.time_to_report = timedelta_to_hours(time_to_report)
            else:
                record.time_to_report = 0

    def compute_nb_reports(self):
        for record in self:
            record.nb_reports = self.env['lims.analysis.report.line'].search_count([('analysis_id', '=', record.id)])

    def get_result_vals(self, parameter_print):
        all_results = self.get_results_from_analysis()
        for result in all_results:
            if result.rel_parameter_print == parameter_print:
                result = self.get_value_of_result_id(result)
                if result.get('rel_type') not in ('done', 'validated', 'cancel'):
                    result.update({'value': ''})
                return result
        return False

    def get_parameter_print_group(self):
        all_results = []
        all_results += self.result_num_ids
        all_results += self.result_sel_ids
        all_results += self.result_compute_ids
        all_results += self.result_text_ids
        print_group = []
        for result in filter(
                lambda r: r.rel_parameter_print and r.rel_parameter_print.print_group_ids and r.print_on_report,
                all_results):
            print_group_title_ids = result.rel_parameter_print.print_group_ids
            for print_group_title in print_group_title_ids:
                if print_group_title and print_group_title not in print_group:
                    print_group += print_group_title
        return_print_group = []
        for group in sorted(print_group, key=lambda x: (x.sequence, x.id)):
            if group not in return_print_group:
                return_print_group += group
        return return_print_group

    def get_report_section_ids(self, groups_ids=False):
        self.ensure_one()
        group_ids = groups_ids or self.get_parameter_print_group()
        return sorted(list({g.section_id for g in group_ids}), key=lambda s: (s.sequence, s.id))

    def get_parameter_print_group_section(self, print_group_ids, section_id=False):
        if not print_group_ids:
            return False
        if section_id:
            print_group_ids = list(set(filter(lambda g: g.section_id and g.section_id == section_id, print_group_ids)))
        else:
            print_group_ids = list(set(filter(lambda g: not g.section_id, print_group_ids)))
        return sorted(print_group_ids, key=lambda x: (x.sequence, x.id))

    def get_value_of_result_id(self, result_id):
        res = super(LimsAnalysis, self).get_value_of_result_id(result_id)
        if result_id.rel_parameter_print:
            res['print_name'] = result_id.rel_parameter_print.print_name
        else:
            res['print_name'] = ''
        res['print_on_report'] = True
        if 'print_on_report' in result_id._fields:
            res['print_on_report'] = result_id.print_on_report
        if 'report_limit_value' in result_id._fields:
            res['report_limit_value'] = result_id.report_limit_value
        if sop_comment := result_id.sop_id.get_external_comment():
            res['sop_id_comment'] = sop_comment
        return res

    def write(self, vals):
        if not self.env.context.get('bypass_check_locked_analysis'):
            self.check_locked_analysis(vals)
        return super(LimsAnalysis, self).write(vals)

    # this function could be overwritten in the repo of the client
    def check_locked_analysis(self, vals):
        locked_analysis = self.sudo().filtered(lambda a: a.is_locked)
        if locked_analysis and not self.env.context.get('force_write') and True in [val not in ALLOWED_VALS for val
                                                                                    in vals]:
            raise exceptions.ValidationError(_(
                "Analyses {} are locked because they are linked to a report in a locked state. "
                "Cancel the report to go further.").format(', '.join(locked_analysis.mapped('name'))))
        return True

    def create_report(self):
        if not len(self.mapped('laboratory_id')) == 1:
            raise UserError(_('You can\'t generate report with analyses from different laboratories'))
        report_line_ids = self.env['lims.analysis.report.line'].search([('analysis_id', 'in', self.ids)])
        if report_line_ids.mapped('report_id').filtered(lambda r: r.state in ('draft', 'validated', 'sent')):
            return {
                'name': 'Confirmation',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'confirmation.create.report',
                'context': {'analysis_ids': self.ids},
                'target': 'new',
            }
        return self.open_wizard_group()

    def open_wizard_group(self):
        if len(self.mapped('partner_id')) <= 1:
            return self.create_analysis_report(True)
        return {
            'name': 'Group',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.group.report',
            'context': {'analysis_ids': self.ids},
            'target': 'new',
        }

    def open_analysis_report(self):
        self.ensure_one()
        report_id = self.env['lims.analysis.report.line'].search([('analysis_id', '=', self.id)]).mapped('report_id')
        return {
            'name': _('Analysis Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.report',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', report_id.ids)],
        }

    def create_analysis_report(self, groupby_customer):
        if self.env.context.get('analysis_ids'):
            analysis_ids = self.browse(self.env.context.get('analysis_ids'))
        else:
            analysis_ids = self
        if not analysis_ids:
            raise exceptions.UserError(_('An analysis at least must be selected to create an analysis report.'))
        report_line_ids = self.env['lims.analysis.report.line'].search([('analysis_id', 'in', analysis_ids.ids)])
        if report_line_ids.mapped('report_id'):
            report_line_ids.mapped('report_id').write({
                'state': 'cancel'
            })
        analysis_customer_dict = {}
        for analysis in analysis_ids:
            if analysis.partner_id in analysis_customer_dict:
                analysis_customer_dict[analysis.partner_id] += analysis
            else:
                analysis_customer_dict[analysis.partner_id] = analysis

        analysis_report_obj = self.env['lims.analysis.report']

        analysis_report_ids = analysis_report_obj
        for analysis_customer in analysis_customer_dict:
            seq = 10
            analysis_vals = []
            for analysis_id in analysis_customer_dict[analysis_customer]:
                analysis_id.date_report = fields.Datetime.now()
                if analysis_id.request_id and not analysis_id.request_id.date_report:
                    analysis_id.request_id.date_report = fields.Datetime.now()
                previous_analysis_report_id = self.env['lims.analysis.report.line'].search(
                    [('analysis_id', '=', analysis_id.id)])
                if previous_analysis_report_id:
                    previous_analysis_report_id = previous_analysis_report_id.mapped('report_id')
                    previous_analysis_report_id = \
                        previous_analysis_report_id.sorted(lambda p: p.create_date, reverse=True)[0]
                vals = (0, 0, {
                    'analysis_id': analysis_id.id,
                    'sequence': seq,
                })

                if groupby_customer:
                    analysis_vals.append(vals)
                    seq += 10
                else:
                    report_vals_to_create = {
                        'name': analysis_id.laboratory_id.seq_report_id.next_by_id(),
                        'partner_id': analysis_id.partner_id.id,
                        'report_analysis_line_ids': [vals],
                        'state': 'draft',
                        'laboratory_id': analysis_id.laboratory_id.id,
                        'customer_ref': analysis_id.customer_ref,
                        'analysis_request_id': analysis_id.request_id.id if analysis_id.request_id else False,
                        'previous_analysis_report_id': previous_analysis_report_id.id if previous_analysis_report_id else False,
                        'external_comment': previous_analysis_report_id and analysis_id.laboratory_id.note_report_replaced or '',
                        'report_id': analysis_id.get_report_id().id if analysis_id.get_report_id() else False,
                        'partner_contact_ids': [Command.link(contact.id) for contact in
                                                analysis_id.partner_contact_ids],
                    }
                    report_vals_to_create.update(analysis_id.get_option_ids())

                    analysis_report_ids += analysis_report_obj.create(report_vals_to_create)

            if groupby_customer:
                analysis_id = analysis_customer_dict[analysis_customer][0]
                report_vals_to_create = {
                    'name': ' ',
                    'partner_id': analysis_id.partner_id.id,
                    'report_analysis_line_ids': analysis_vals,
                    'state': 'draft',
                    'laboratory_id': analysis_id.laboratory_id.id,
                    'customer_ref': analysis_id.customer_ref,
                    'analysis_request_id': analysis_id.request_id.id if analysis_id.request_id else False,
                    'previous_analysis_report_id': previous_analysis_report_id.id if previous_analysis_report_id else False,
                    'external_comment': previous_analysis_report_id and analysis_id.laboratory_id.note_report_replaced or '',
                    'report_id': analysis_id.get_report_id().id if analysis_id.get_report_id() else False,
                    'partner_contact_ids': [Command.link(contact.id) for contact in
                                            analysis_customer_dict[analysis_customer].partner_contact_ids],
                }
                report_vals_to_create.update(analysis_id.get_option_ids())
                report_id = analysis_report_obj.create(report_vals_to_create)
                report_id.name = analysis_id.laboratory_id.seq_report_id.next_by_id() if (
                    analysis_id.laboratory_id.seq_report_id
                ) else report_id.id
                analysis_report_ids += report_id

        return {
            'name': 'Analysis Report',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', analysis_report_ids.ids)],
            'res_model': 'lims.analysis.report',
            'view_mode': 'tree,form',
        }

    def toggle_active(self):
        return super(LimsAnalysis, self.with_context(force_write=True)).toggle_active()

    def is_empty_html_field(self, html_field):
        return not html2plaintext(html_field) != u''

    def get_report_id(self):
        """
        This function retrieves the report template,
        we check if a template is defined on the request before retrieving
        the default report template of the laboratory

        :return:
        """
        report_id = False
        if self.request_id and self.request_id.report_template_id:
            report_id = self.request_id.report_template_id.report_id
        elif self.laboratory_id:
            report_id = self.laboratory_id.get_default_report_model_id()
        return report_id

    def get_option_ids(self):
        """
        This function retrieves the options defined in the report template,
        we check if a template is defined on the request before retrieving
        the default report template of the laboratory

        :return:
        """
        option_ids = {}
        if self.request_id and self.request_id.report_template_id:
            option_ids = self.request_id.report_template_id.get_dict_for_selected_options(
                self.request_id.report_template_id.option_ids)
        elif self.laboratory_id and self.laboratory_id.default_report_template:
            option_ids = self.laboratory_id.default_report_template.get_dict_for_selected_options(
                self.laboratory_id.default_report_template.option_ids)
        return option_ids

    def get_sent_reports(self, report_state=False, get_only_if_one=False):
        self.ensure_one()
        if not report_state:
            report_state = 'sent'
        report_line_ids = self.env['lims.analysis.report.line'].search(
            [('analysis_id.id', '=', self.id), ('report_id.state', '=', report_state)])
        report_ids = report_line_ids.report_id
        if get_only_if_one:
            return report_ids if report_ids and len(report_ids) == 1 else False
        return report_ids

    def get_limited_value(self, result_id, val_formula, digits):
        """
        Override method from lims_base to return field report_limit_value instead of generating text from limits if
        report limit value exists on result
        :return: report limit value of result or super
        """
        if result_id.report_limit_value:
            decision_limit_id = result_id.decision_limit_result_id if result_id.method_param_charac_id.format in [
                'nu', 'ca'] else False
            return result_id.report_limit_value, decision_limit_id
        else:
            return super().get_limited_value(result_id, val_formula, digits)
