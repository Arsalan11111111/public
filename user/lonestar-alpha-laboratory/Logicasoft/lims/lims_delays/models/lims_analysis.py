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
from odoo import fields, models, api, _, tools, exceptions
from datetime import datetime, timedelta


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    date_change = fields.Boolean('Date change', readonly=True, copy=False,
                                 help="Date change is marked if 'Change Date Sample' button has been used")
    commercial_lead_date = fields.Datetime(string='Commercial lead date',
                                           help='If this analysis is not completed on time, it will be marked as '
                                                '\'out of time\'. this date is calculated from the pack of this '
                                                'analysis which has the longest commercial lead time.',
                                           copy=False)
    commercial_warning_date = fields.Datetime(string='Commercial warning date',
                                              help='If this analysis is not completed before the warning date, '
                                                   'it will be marked as \'warning time\'. this date is calculated '
                                                   'with the warning time from the pack of this analysis which has '
                                                   'the longest commercial lead time.',
                                              copy=False)
    is_commercial_out_of_time = fields.Boolean('Commercial out of time',
                                               help='Mark this analysis as \' commercially out of time\'.', copy=False,
                                               tracking=True)
    reason_change = fields.Char(tracking=True)

    def get_value_of_result_id(self, result_id):
        res = super(LimsAnalysis, self).get_value_of_result_id(result_id)
        res['is_technical_out_of_time'] = result_id.is_technical_out_of_time
        if result_id.is_technical_out_of_time:
            html_class = res.get('html_class', '')
            res.update({
                'html_class': html_class + ' result_is_out_of_time'
            })
        return res

    def get_analysis_to_check_compute(self):
        return self.sudo().search([('date_sample_receipt', '!=', False), ('rel_type', 'in', ['plan', 'todo', 'wip'])])

    def get_out_of_time(self):
        return self.filtered(lambda a: a.commercial_lead_date and
                                       a.commercial_lead_date <= fields.Datetime.now() and not
                                       a.is_commercial_out_of_time)

    def get_in_time(self):
        return self.filtered(lambda a: not a.commercial_lead_date or
                                       (a.commercial_lead_date > fields.Datetime.now() and
                                        a.is_commercial_out_of_time))

    def check_analysis_time(self):
        # Can call the function from cron (self is empty) or function (self isn't empty)
        analysis_ids = self
        if not analysis_ids:
            analysis_ids = self.get_analysis_to_check_compute()
        out_analysis_ids = analysis_ids.get_out_of_time()
        if out_analysis_ids:
            out_analysis_ids.write({
                'is_commercial_out_of_time': True
            })
        in_analysis_ids = analysis_ids.get_in_time()
        if in_analysis_ids:
            in_analysis_ids.write({
                'is_commercial_out_of_time': False,
            })

    def recompute_delay_results(self):
        for record in self:
            for result_id in record.result_num_ids:
                delay_vals = record.get_delays()
                result_id.update(delay_vals)
            for sel_result_id in record.result_sel_ids:
                delay_vals = record.get_delays()
                sel_result_id.update(delay_vals)
            for compute_result_id in record.result_compute_ids:
                delay_vals = record.get_delays()
                compute_result_id.update(delay_vals)
            for text_result_id in record.result_text_ids:
                delay_vals = record.get_delays()
                text_result_id.update(delay_vals)

    def do_todo(self):
        for record in self:
            date_for_check = record.laboratory_id.date_for_compute_warning_time
            if date_for_check and date_for_check == 'sample':
                if not record.date_sample:
                    raise exceptions.ValidationError(_('Sample date must be filled'))
            elif not record.date_sample_receipt:
                raise exceptions.ValidationError(_('Date sample receipt must be filled'))
        return super(LimsAnalysis, self).do_todo()

    def wizard_set_date_sample(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'change.date.sample.analysis',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_analysis_id': self.id,
                'default_date_sample': self.date_sample,
                'default_date_sample_receipt': self.date_sample_receipt,
            },
        }

    def set_date_sample(self, reason, date_sample, date_sample_receipt):
        """
        Function called by 'Change date sample analysis' wizard. Change dates used on delay calculation and recompute
        time-outs on results ans tests
        :param reason: Reason of the rework (char)
        :param date_sample: date_sample of analysis
        :param date_sample_receipt: date_sample_receipt of analysis
        :return:
        """
        self.write({
            'date_sample': date_sample,
            'date_sample_receipt': date_sample_receipt,
            'date_change': True,
            'reason_change': reason,
        })
        date_for_compute = self.laboratory_id.get_date_begin_delays()
        if self.result_num_ids:
            self.result_num_ids.check_out_of_time(date_for_compute)
        if self.result_sel_ids:
            self.result_sel_ids.check_out_of_time(date_for_compute)
        if self.result_compute_ids:
            self.result_compute_ids.check_out_of_time(date_for_compute)
        if self.result_text_ids:
            self.result_text_ids.check_out_of_time(date_for_compute)
        self.sop_ids.with_context(reset_dates=True).update_date_delay()
        return True

    def get_sop_vals(self, method_id):
        """
        Original method update due_date of sop according to due_date of analysis. But in this module, the due_date of
        sop is calculated according to the due time of the method.
        :param method_vals:
        :param method_id:
        :return: dict
        """
        res = super(LimsAnalysis, self).get_sop_vals(method_id)
        if res:
            res.update({
                'due_date': False,
            })
        return res

    def get_time_out_calendar(self):
        return self.laboratory_id.resource_calendar_id

    def get_max_duration(self):
        max_pack = self.pack_ids.sorted(key=lambda p: p.commercial_lead_time, reverse=True)[0]
        if max_pack:
            return max_pack.commercial_lead_time, max_pack.commercial_warning_time
        return 0, 0

    def get_base_date_for_timeout(self):
        return self.date_sample_receipt

    def get_commercial_delay_dates(self, base_date, commercial_lead_duration, commercial_warning_duration,
                                   resource_calendar_id=False):
        commercial_lead_date = base_date + commercial_lead_duration
        commercial_warning_date = base_date + commercial_warning_duration
        if resource_calendar_id:
            nb_days = 1
            total_days = (commercial_lead_date - base_date).days
            if resource_calendar_id:
                for i in range(0, total_days, 1):
                    i_date = base_date + timedelta(days=nb_days)
                    computed_date = self.check_if_pass_day(i_date, resource_calendar_id)
                    passed_days = computed_date - i_date
                    nb_days += passed_days.days
                    if i_date <= commercial_warning_date:
                        commercial_warning_date += passed_days
                    commercial_lead_date += passed_days
                    nb_days += 1

    def compute_analysis_due_date(self):
        """
        Calculate commercial lead date and commercial warning date of analysis according to this rule :
        Calculation is based on the parameter pack with the highest lead time, and the sample reception date
        Analysis commercial lead date = date of sample receipt + commercial lead time
        Analysis commercial warning date = date of sample receipt + commercial lead time - commercial warning time
        Closing days (= weekends or public holidays) should not appear in counting. Those are determined based on the
        resource calendar configured for the laboratory
        """
        for record in self:
            commercial_lead_date = False
            commercial_warning_date = False
            max_duration, warning_time = record.get_max_duration()
            if max_duration > 0.0:
                resource_calendar_id = record.get_time_out_calendar()
                max_duration_in_seconds = max_duration * 3600
                commercial_lead_duration = timedelta(seconds=max_duration_in_seconds)
                commercial_warning_duration = timedelta(seconds=max_duration_in_seconds) - \
                                              timedelta(seconds=warning_time * 3600)
                base_date = record.get_base_date_for_timeout()
                commercial_lead_date, commercial_warning_date = record.get_commercial_delay_dates(
                    base_date, commercial_lead_duration, commercial_warning_duration, resource_calendar_id)
            record.update({
                'commercial_lead_date': commercial_lead_date,
                'commercial_warning_date': commercial_warning_date,
            })
        self.check_analysis_time()

    def check_if_pass_day(self, i_date, resource_calendar_id):
        """
        If there's a day of week-end/public holiday in between the sample reception and the due date of analysis, it
        shouldn't count (ex. due date tomorrow but it's friday => due date should be monday and not saturday)
        :param i_date: date that has to be checked
        :param resource_calendar_id: resource.calendar that determines which day is week-end/holiday
        :return: the next day that is not week-end/holiday
        """
        weekday = i_date.weekday()
        pass_day = False
        if str(weekday) not in resource_calendar_id.attendance_ids.mapped('dayofweek'):
            pass_day = True
        else:
            leave_id = resource_calendar_id.global_leave_ids.filtered(
                lambda l: fields.Date.from_string(l.date_from) <= i_date.date() <=
                          fields.Date.from_string(l.date_to))
            if leave_id:
                pass_day = True
        if pass_day:
            i_date += timedelta(days=1)
            i_date = self.check_if_pass_day(i_date, resource_calendar_id)
        return i_date
