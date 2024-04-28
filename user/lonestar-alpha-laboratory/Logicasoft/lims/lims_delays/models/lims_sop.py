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
from odoo import fields, models, api
from datetime import timedelta, datetime, MAXYEAR
import sys


class LimsSop(models.Model):
    _inherit = 'lims.sop'

    technical_lead_date = fields.Datetime(string='Technical lead date',
                                          help='If this test is not completed on time, it will be marked as '
                                               '\'out of time\'. this date is calculated from the parameter from this '
                                               'test which has the shortest technical lead time.', store=True,
                                          copy=False)
    technical_warning_date = fields.Datetime(string='Technical warning date',
                                             help='If this test is not completed before the warning date, '
                                                  'it will be marked as \'warning time\'. this date is calculated '
                                                  'with the warning time from the parameter from this test which has '
                                                  'the shortest technical lead time.', store=True,
                                             copy=False)
    technical_warning_time = fields.Float(string='Technical warning time',
                                          help='Technical lead time with the shortest duration found in the set of '
                                               'parameters')
    technical_lead_time = fields.Float(string='Technical lead time',
                                       help='Technical warning time from technical lead time with the shortest '
                                            'duration found in the set of parameters')
    is_technical_out_of_time = fields.Boolean('Technical out of time', compute='compute_result_out_of_time', store=True,
                                              tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        """
        When create SOP set the smallest technical lead time and technical warning time from the result
        :param vals:
        :return:
        """
        sops = super().create(vals_list)
        for sop in sops:
            technical_lead_time = sop.technical_lead_time
            technical_warning_time = sop.technical_warning_time
            if sop.result_num_ids:
                technical_lead_time, technical_warning_time = self.sudo().get_smallest_time(sop.result_num_ids,
                                                                                            technical_lead_time,
                                                                                            technical_warning_time)
            if sop.result_sel_ids:
                technical_lead_time, technical_warning_time = self.sudo().get_smallest_time(sop.result_sel_ids,
                                                                                            technical_lead_time,
                                                                                            technical_warning_time)
            if sop.result_compute_ids:
                technical_lead_time, technical_warning_time = self.sudo().get_smallest_time(sop.result_compute_ids,
                                                                                            technical_lead_time,
                                                                                            technical_warning_time)
            if sop.result_text_ids:
                technical_lead_time, technical_warning_time = self.sudo().get_smallest_time(sop.result_text_ids,
                                                                                            technical_lead_time,
                                                                                            technical_warning_time)
            sop.technical_lead_time = technical_lead_time
            sop.technical_warning_time = technical_warning_time
        return sops

    def get_smallest_time(self, result_ids, technical_lead_time, technical_warning_time):
        """
        Search and return the smallest value lead_time, and warning_time in list of results
        :param result_ids: list of result
        :param lead_time: float
        :param warning_time: float
        :return: float, float
        """
        if technical_lead_time == 0:
            technical_lead_time = sys.maxsize
        for result in result_ids:
            if result.technical_lead_time < technical_lead_time:
                technical_lead_time = result.technical_lead_time
                technical_warning_time = result.technical_warning_time
        return technical_lead_time, technical_warning_time

    def get_smallest_date(self, result_ids, technical_lead_date=False, technical_warning_date=False):
        """
        Search and return the smallest value lead_date, and warning_date in list of results
        :param result_ids: list of result
        :param lead_date: datetime
        :param warning_date: datetime
        :return: datetime, datetime
        """
        for result in result_ids:
            if not technical_lead_date or (result.technical_lead_date and
                                           result.technical_lead_date < technical_lead_date):
                technical_lead_date = result.technical_lead_date
                technical_warning_date = result.technical_warning_date
        return technical_lead_date, technical_warning_date

    @api.depends('result_num_ids', 'result_num_ids.is_technical_out_of_time',
                 'result_sel_ids', 'result_sel_ids.is_technical_out_of_time',
                 'result_compute_ids', 'result_compute_ids.is_technical_out_of_time',
                 'result_text_ids', 'result_text_ids.is_technical_out_of_time')
    def compute_result_out_of_time(self):
        """
        Check if on result is out or grace or delay, if there is one set the same value in SOP
        :return:
        """
        self = self.sudo()
        domain = [('sop_id', 'in', self.ids), ('is_technical_out_of_time', '=', True)]
        result = self.env['lims.analysis.numeric.result'].sudo().search(domain)
        sel = self.env['lims.analysis.sel.result'].sudo().search(domain)
        compute = self.env['lims.analysis.compute.result'].sudo().search(domain)
        text_result = self.env['lims.analysis.text.result'].sudo().search(domain)
        for record in self:
            if any(result.filtered(lambda x: x.sop_id.id == record.id)) \
                    or any(sel.filtered(lambda x: x.sop_id.id == record.id)) \
                    or any(text_result.filtered(lambda x: x.sop_id.id == record.id)) \
                    or any(compute.filtered(lambda x: x.sop_id.id == record.id)):
                record.is_technical_out_of_time = True
            else:
                record.is_technical_out_of_time = False

    def do_todo(self):
        res = super(LimsSop, self).do_todo()
        self.action_check_out_of_time()
        for record in self:
            delay_vals = record.get_smallest_date_in_results()
            record.write(delay_vals)
        return res

    def get_smallest_date_in_results(self):
        self.ensure_one()
        if not self.env.context.get('reset_dates'):
            technical_lead_date = self.technical_lead_date
            technical_warning_date = self.technical_warning_date
        else:
            technical_lead_date = technical_warning_date = False
        if self.result_num_ids:
            technical_lead_date, technical_warning_date = self.sudo().get_smallest_date(self.result_num_ids,
                                                                                        technical_lead_date,
                                                                                        technical_warning_date)
        if self.result_sel_ids:
            technical_lead_date, technical_warning_date = self.sudo().get_smallest_date(self.result_sel_ids,
                                                                                        technical_lead_date,
                                                                                        technical_warning_date)
        if self.result_compute_ids:
            technical_lead_date, technical_warning_date = self.sudo().get_smallest_date(self.result_compute_ids,
                                                                                        technical_lead_date,
                                                                                        technical_warning_date)
        if self.result_text_ids:
            technical_lead_date, technical_warning_date = self.sudo().get_smallest_date(self.result_text_ids,
                                                                                        technical_lead_date,
                                                                                        technical_warning_date)
        return {
            'technical_lead_date': technical_lead_date,
            'technical_warning_date': technical_warning_date
        }

    def get_result_stage_for_delays(self):
        """
        Return the stages of results on which delay calculations must be applied
        By default stage todo
        :returns Recordset of result stages
        """
        return self.env['lims.result.stage'].search([('type', '=', 'todo')])

    def action_check_out_of_time(self):
        result_obj = self.env['lims.analysis.numeric.result']
        result_sel_obj = self.env['lims.analysis.sel.result']
        result_cp_obj = self.env['lims.analysis.compute.result']
        result_txt_obj = self.env['lims.analysis.text.result']
        stage_ids = self.get_result_stage_for_delays()
        date_begin_delays = self.env['lims.laboratory'].get_date_begin_delays()
        if self:
            result_num_ids = self.result_num_ids
            result_sel_ids = self.result_sel_ids
            result_cp_ids = self.result_compute_ids
            result_txt_ids = self.result_text_ids
        else:
            domain = [
                ('stage_id', 'in', stage_ids.ids),
                ('technical_lead_time', '>', 0),
            ]
            result_num_ids = result_obj.search(domain)
            result_sel_ids = result_sel_obj.search(domain)
            result_cp_ids = result_cp_obj.search(domain)
            result_txt_ids = result_txt_obj.search(domain)
        if result_num_ids:
            result_num_ids.check_out_of_time(date_begin_delays)
        if result_sel_ids:
            result_sel_ids.check_out_of_time(date_begin_delays)
        if result_cp_ids:
            result_cp_ids.check_out_of_time(date_begin_delays)
        if result_txt_ids:
            result_txt_ids.check_out_of_time(date_begin_delays)

    def update_date_delay(self):
        for record in self:
            delay_values = record.get_smallest_date_in_results()
            record.update(delay_values)
