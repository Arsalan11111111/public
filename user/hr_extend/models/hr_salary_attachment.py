from odoo.exceptions import AccessError, ValidationError
import pytz
from datetime import timedelta
from collections import defaultdict
from datetime import datetime, date, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import calendar

PAY_SCALE_RANGES = {
    '100%': 21,
    '75%': 14,  # 35 - 21
    '50%': 35,  # 70 - 35
    '35%': 112,  # 182 - 70
}

class HrGrade(models.Model):
    _name = 'hr.grade'

    name = fields.Char("Employee Grade")

class HrEmployees(models.Model):
    _inherit = 'hr.employee'

    grades = fields.Many2one('hr.grade',"Employee Grade")

class HrSalaryAttachment(models.Model):
    _inherit = 'hr.salary.attachment'

    description_type_id = fields.Many2one('hr.description.type', string="Description Type")

    @api.constrains('description_type_id')
    def _check_user_permission(self):
        user = self.env.user
        if user not in self.description_type_id.permission_ids:
            raise ValidationError(_("You have not permissions to create This '%s'.") % (self.description_type_id.name))


class HrDescriptionType(models.Model):
    _name = 'hr.description.type'
    _description = "Hr Description Type"

    name = fields.Char(string="Description")
    permission_ids = fields.Many2many('res.users', string="Create/Write Access Users")
    view_access = fields.Many2many('res.users', 'hr_dec_user_rel','desc_id', 'user_id', string="View Access Users")

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                holiday.number_of_days = holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
                days = holiday.date_to - holiday.date_from

                holiday.number_of_days = days.days + 1
            else:
                holiday.number_of_days = 0


class HrContract(models.Model):
    _inherit = 'hr.contract'

    bank_account_id = fields.Many2one(related="employee_id.bank_account_id")
    grades = fields.Many2one('hr.grade',"Employee Grade",compute="_get_employee_grade")
    gross_salary = fields.Monetary('Gross Salary', compute="_compute_gross_salary" , help="Employee's monthly gross wage.")
    airticket = fields.Monetary('Air Ticket Allowances', help="Employee's air ticket allowance", default=0)
    def _compute_gross_salary(self):
        for rec in self:
            rec.gross_salary = rec.wage + rec.l10n_ae_housing_allowance + rec.l10n_ae_transportation_allowance + rec.l10n_ae_other_allowances + \
            + rec.airticket

    def _get_employee_grade(self):
        for rec in self:

            if rec.employee_id:
                if rec.employee_id.bank_account_id:
                    rec.bank_account_id = rec.employee_id.bank_account_id
                if rec.employee_id.grades:
                    rec.grades = rec.employee_id.grades
                else:
                    rec.grades = None
            else:
                rec.grades = None

    def _generate_work_entries(self, date_start, date_stop, force=False):
        date_start = datetime.combine(date_start, datetime.min.time())
        date_stop = datetime.combine(date_stop, datetime.min.time())
        return super(HrContract, self)._generate_work_entries(date_start,date_stop)

    def _get_work_hours(self, date_from, date_to, domain=None):
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.min.time())
        return super(HrContract, self)._get_work_hours(date_from,date_to)

class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    no_of_days = fields.Float("No Of Month", compute="_get_total_duration_of_month")
    no_of_unpaid_leaves = fields.Float("Unpaid Leaves",compute= "_get_total_duration_of_unpaid_leaves")
    cut_unpaid_leaves = fields.Float("Unpaid amount",compute="_get_total_amount_unpaid")
    sick_leaves_formula = fields.Float("Sick Leaves Formula",compute="_get_total_sick_leaves_with_formula")
    sick_leaves_deduction = fields.Float("Check")
    employee_badge = fields.Char(related="employee_id.barcode")
    employee_badge_id = fields.Char("Badge ID")
    gross_salary = fields.Float(compute="_get_gross_salary", string="Gross Salary")
    no_of_days_worked = fields.Float("No of days Worked", compute="_get_no_of_days_worked")
    gross_salary2 = fields.Float("GS2",compute="_get_gross_salary2")
    gross_salary3 = fields.Float("GS3",compute="_get_gross_salary3")
    def _get_gross_salary(self):
        for rec in self:
            rec.gross_salary = rec.contract_id.gross_salary
            rec.gross_salary2 = (rec.contract_id.gross_salary/rec.no_of_days)*rec.no_of_days_worked
            rec.employee_badge_id = rec.employee_badge
    def _get_gross_salary2(self):
        for rec in self:
            rec.gross_salary2 = (rec.contract_id.gross_salary/rec.no_of_days)*rec.no_of_days_worked

    def _get_gross_salary3(self):
        for rec in self:
            overtime = 0
            allowance = 0
            reimbursement = 0
            for lines in rec.line_ids:
                if lines.code == 'OVERTIME':
                    overtime = lines.amount
                    break
                if lines.code == 'TEMPALLOWANCE':
                    allowance = lines.amount
                if lines.code == 'REIMBURSEMENT':
                    reimbursement = lines.amount

            rec.gross_salary3 = rec.gross_salary2 + overtime + allowance + reimbursement
    def _get_no_of_days_worked(self):
        for rec in self:

            leaves = self.env['hr.leave'].search(
                [('request_date_from', '>=', rec.date_from), ('request_date_to', '<=', rec.date_to),
                 ('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate')])
            leaves_days = 0
            if leaves:
                for leave in leaves:

                    if leave.holiday_status_id.display_name == 'Unpaid':
                        leaves_days = leaves.number_of_days
                    else:
                        leaves_days = 0.0

            rec.no_of_days_worked = rec.no_of_days - leaves_days
    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': day_rounded,
                'number_of_hours': hours,
            }
            res.append(attendance_line)
        return res

    def _get_total_duration_of_month(self):
        for rec in self:
            if rec.date_to and rec.date_from:
                rec.no_of_days = (rec.date_to - rec.date_from).days + 1
            else:
                rec.no_of_days = 0.0

    def _get_total_duration_of_unpaid_leaves(self):
          for rec in self:
            total_unpaid_days = 0.0
            for worked_day in rec.worked_days_line_ids:
                if worked_day.name == "Unpaid":
                    total_unpaid_days += worked_day.number_of_days
            rec.no_of_unpaid_leaves = total_unpaid_days

    def _get_total_amount_unpaid(self):
        for rec in self:
            leaves = self.env['hr.leave'].search(
                [('request_date_from', '>=', rec.date_from), ('request_date_to', '<=', rec.date_to),('employee_id','=',rec.employee_id.id),('state','=','validate')])
            if leaves:
                for leave in leaves:

                    if leave.holiday_status_id.display_name =='Unpaid':
                        rec.cut_unpaid_leaves = leaves.number_of_days
                    else:
                        rec.cut_unpaid_leaves = 0.0
            else:
                rec.cut_unpaid_leaves =  0.0

    def calculate_sick_leave_deduction_previous(self,previous_leaves_taken):
        total_leaves = previous_leaves_taken
        deductions = {'100%': 0, '75%': 0, '50%': 0, '35%': 0}

        if total_leaves <= 21:
            deductions['100%'] = total_leaves
        elif total_leaves <= 35:
            deductions['100%'] = 21
            deductions['75%'] = total_leaves - 21
        elif total_leaves <= 70:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = total_leaves - 35
        elif total_leaves <= 182:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = 35
            deductions['35%'] = total_leaves - 70
        else:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = 35
            deductions['35%'] = 112  # Maximum 182 - 70 days

        return deductions
    def calculate_sick_leave_deduction(self,previous_leaves_taken, this_month_sick_leaves):
        total_leaves = previous_leaves_taken + this_month_sick_leaves
        deductions = {'100%': 0, '75%': 0, '50%': 0, '35%': 0}

        if total_leaves <= 21:
            deductions['100%'] = total_leaves
        elif total_leaves <= 35:
            deductions['100%'] = 21
            deductions['75%'] = total_leaves - 21
        elif total_leaves <= 70:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = total_leaves - 35
        elif total_leaves <= 182:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = 35
            deductions['35%'] = total_leaves - 70
        else:
            deductions['100%'] = 21
            deductions['75%'] = 14
            deductions['50%'] = 35
            deductions['35%'] = 112  # Maximum 182 - 70 days

        return deductions

    def subtract_deductions(self, previous_month_deductions, current_month_deductions):
        result = {}

        for tier in current_month_deductions:
            if tier in previous_month_deductions:
                result[tier] = current_month_deductions[tier] - previous_month_deductions[tier]
            else:
                result[tier] = current_month_deductions[tier]

        return result
    # Example usage:

    def _get_total_sick_leaves_with_formula(self):
        for rec in self:
            current_year = datetime.now().year
            first_day_of_year = datetime(current_year, 1, 1).date()

            sick_leaves_total = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
                                                             ('request_date_from', '>=', first_day_of_year),
                                                             ('request_date_to', '<=', rec.date_to),
                                                             ('holiday_status_id.name', '=', 'Sick Time Off')])
            number_of_days_total = sum(leave.number_of_days for leave in sick_leaves_total)
            total_deduction = 0
            if number_of_days_total > 0.0:
                sick_leaves_month = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
                                                                 ('date_from', '>=', rec.date_from),
                                                                 ('date_to', '<=', rec.date_to),
                                                                 ('holiday_status_id.name', '=', 'Sick Time Off')])
                this_month_sick_leaves = sum(leaves.number_of_days for leaves in sick_leaves_month)


                if this_month_sick_leaves > 0.0:
                    previous_leaves_taken = number_of_days_total - this_month_sick_leaves
                    previous_month = self.calculate_sick_leave_deduction_previous(previous_leaves_taken)
                    deductions = self.calculate_sick_leave_deduction(previous_leaves_taken, this_month_sick_leaves)
                    remaining_deductions = self.subtract_deductions(previous_month, deductions)
                    all_zero = all(value != 0 for value in remaining_deductions.values())
                    if not all_zero:
                        no_of_days_in_month = (rec.date_to - rec.date_from).days + 1
                        gross_amount = 0
                        for gross in rec.line_ids:
                            if gross.code == 'GROSS':
                                gross_amount = gross.amount
                                break
                        total_deduction = 0
                        for percentage, days in remaining_deductions.items():
                            if days != 0:
                                # Calculate deduction amount based on the percentage, number of days, and gross amount
                                deduction_percentage = float(100 - int(percentage.strip('%')))
                                deduction_amount = deduction_percentage / 100 * gross_amount * days / no_of_days_in_month
                                total_deduction += deduction_amount
                        # total_deduction = total_deduction + gross_amount
                        total_deduction = total_deduction
                        print("Total deduction amount:", round(total_deduction, 2))
                        rec.sick_leaves_formula = total_deduction
                        rec.sick_leaves_deduction = total_deduction
                    else:
                        if total_deduction == 0:
                            rec.sick_leaves_formula = 0.0
                            rec.sick_leaves_deduction = 0.0
                        else:
                            rec.sick_leaves_formula = total_deduction
                            rec.sick_leaves_deduction = total_deduction
                    if total_deduction == 0:
                        rec.sick_leaves_formula = 0.0
                        rec.sick_leaves_deduction = 0.0
                    else:
                        rec.sick_leaves_formula = total_deduction
                        rec.sick_leaves_deduction = total_deduction
                else:
                    if total_deduction == 0:
                        rec.sick_leaves_formula = 0.0
                        rec.sick_leaves_deduction = 0.0
                    else:
                        rec.sick_leaves_formula = total_deduction
                        rec.sick_leaves_deduction = total_deduction
            else:
                if total_deduction == 0:
                    rec.sick_leaves_formula = 0.0
                    rec.sick_leaves_deduction = 0.0
                else:
                    rec.sick_leaves_formula = total_deduction
                    rec.sick_leaves_deduction = total_deduction
