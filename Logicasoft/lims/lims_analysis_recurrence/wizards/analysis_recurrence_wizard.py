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
from odoo import fields, models, exceptions, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from calendar import monthrange

from odoo.tools.safe_eval import safe_eval

days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


class AnalysisRecurrenceWizard(models.TransientModel):
    _name = 'analysis.recurrence.wizard'
    _description = 'Analysis Recurrence Wizard'

    def get_day_in_month(self):
        return [(str(x), str(x)) for x in range(1, 32)]

    analysis_id = fields.Many2one('lims.analysis', string='Original analysis', readonly=True)
    interval = fields.Integer('Interval', required=True, default=1)
    rrule_type = fields.Selection(
        [('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')], 'Period',
        required=True)
    end_type = fields.Selection([('count', 'Number of repetitions'), ('end_date', 'End date')], 'Until', required=True,
                                default='count')
    count = fields.Integer('Count', required=True, default=1)
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('saturday')
    sunday = fields.Boolean('Sunday')
    month_by = fields.Selection([('date', 'Date of month'), ('day', 'Day of month')], 'Option')
    day = fields.Selection(selection="get_day_in_month", string='Date of month')
    week_list = fields.Selection([('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
                                  ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'),
                                  ('sunday', 'Sunday')], 'Weekday')
    byday = fields.Selection([('1', 'First'), ('2', 'Second'), ('3', 'Third'), ('4', 'Fourth'),
                              ('5', 'Fifth'), ('-1', 'Last')], 'By day')
    date_end = fields.Date('Repeat Until')

    def get_default_date_end(self, unit, interval, count):
        res_date = fields.Date.from_string(fields.Date.today())
        units_to_add = interval * count
        if unit == 'daily':
            res_date += relativedelta(days=units_to_add)
        elif unit == 'weekly':
            res_date += relativedelta(weeks=units_to_add)
        elif unit == 'monthly':
            res_date += relativedelta(months=units_to_add)
        elif unit == 'yearly':
            res_date += relativedelta(years=units_to_add)
        res_date += relativedelta(days=1)
        return datetime.strptime(str(res_date), "%Y-%m-%d")

    def create_analysis(self, vals):
        self.analysis_id.copy(default=vals)

    def calculate_date(self, date=False, unit=False, amount=0):
        if date and unit:
            res_date = date
            if unit == 'daily':
                res_date += relativedelta(days=amount)
            elif unit == 'weekly':
                res_date += relativedelta(weeks=amount)
            elif unit == 'monthly':
                res_date += relativedelta(months=amount)
            else:
                res_date += relativedelta(years=amount)
            return res_date
        return False

    def check_date_selected(self):
        return any(safe_eval(f'self.{d}', {'self': self}) for d in days)

    def create_recurrence(self):
        # check
        if self.interval < 1:
            raise exceptions.ValidationError('Interval should be greater than 0')
        if self.end_type == 'count' and self.count < 1:
            raise exceptions.ValidationError('Repetition should be greater than 0')
        elif self.end_type == 'date' and self.date_end < fields.Date.today():
            raise exceptions.ValidationError('Date end should be greater than today')
        if self.rrule_type == 'weekly' and not self.check_date_selected():
            raise exceptions.ValidationError('At least one day should be selected')

        # Initialization
        vals = self.analysis_id.get_vals_for_recurrence()
        date_end = self.date_end and datetime.strptime(str(self.date_end), "%Y-%m-%d")
        deadline = self.analysis_id.date_start
        deadline = datetime.strptime(str(deadline.date()), "%Y-%m-%d") \
            if deadline else datetime.now()
        deadline = deadline.replace(hour=0, minute=0, second=0, microsecond=0)
        count = self.count if self.end_type == 'count' else 1
        nb_create = 0
        # Treatment
        for x in range(0, count):
            if self.rrule_type in ['daily', 'yearly'] or (self.rrule_type == 'monthly' and not self.month_by):
                if self.end_type == 'count':
                    deadline = self.calculate_date(deadline, self.rrule_type, self.interval)
                    vals['date_plan'] = deadline
                    self.create_analysis(vals)
                    nb_create += 1
                else:
                    while deadline < date_end:
                        deadline = self.calculate_date(deadline, self.rrule_type, self.interval)
                        vals['date_plan'] = deadline
                        self.create_analysis(vals)
                        nb_create += 1
            elif self.rrule_type == 'monthly' and self.month_by:
                if self.month_by == 'date':
                    date_end = self.get_default_date_end(self.rrule_type, self.interval, self.count)\
                        if not date_end else date_end
                    while deadline < date_end:
                        deadline = self.calculate_date(deadline, self.rrule_type, self.interval)
                        this_date_ok = False
                        aux_date = deadline
                        chosen_day = self.day
                        while not this_date_ok:
                            datee = str(aux_date.year) + '-' + str(aux_date.month) + '-' + chosen_day
                            try:
                                aux_date = datetime.date(datetime.strptime(datee, "%Y-%m-%d"))
                            except ValueError:
                                chosen_day = str(int(chosen_day) - 1)
                            else:
                                this_date_ok = True
                        vals['date_plan'] = deadline
                        self.create_analysis(vals)
                        nb_create += 1
                else:
                    if not date_end:
                        date_end = self.get_default_date_end(self.rrule_type, self.interval, self.count)
                    while deadline < date_end:
                        deadline = self.calculate_date(deadline, self.rrule_type, self.interval)
                        # Let's get the list of dates for the required weekday
                        aux_weekday = days.index(self.week_list)
                        aux_days = []
                        for d in range(0, monthrange(deadline.year, deadline.month)[1]):
                            datee = str(deadline.year) + '-' + str(deadline.month) + '-' + str(d+1)
                            aux_date = datetime.date(datetime.strptime(datee, "%Y-%m-%d"))
                            if aux_date.weekday() == aux_weekday:
                                aux_days.append(aux_date)

                        if self.byday == '-1':
                            aux_by_day = -1
                        else:
                            aux_by_day = int(self.byday) - 1
                        aux_deadline = aux_days[aux_by_day]
                        vals['date_plan'] = aux_deadline
                        self.create_analysis(vals)
            elif self.rrule_type == 'weekly':
                date_ok = True
                while date_ok:
                    deadline = self.calculate_date(deadline, self.rrule_type, self.interval)
                    deadline_weekday = deadline.weekday()
                    if (self.end_type != ' count' and date_end and deadline <= date_end) or self.end_type == 'count':
                        for d in range(0, len(days)):
                            aux_deadline = deadline
                            if safe_eval('self.' + days[d], {'self': self}):
                                if deadline_weekday <= d:
                                    days_to_add = (d - deadline_weekday)
                                else:
                                    days_to_add = 7 - (deadline_weekday - d)
                                aux_deadline += relativedelta(days=days_to_add)
                                vals['date_plan'] = aux_deadline
                                self.create_analysis(vals)
                                nb_create += 1
                        if self.end_type == 'count':
                            date_ok = False
                    else:
                        date_ok = False
        create_ids = self.env['lims.analysis'].search([], order="id desc", limit=nb_create)
        return {
            'name': _('Analysis created'),
            'domain': [('id', 'in', create_ids.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'context': {},
            'target': 'current',
        }
