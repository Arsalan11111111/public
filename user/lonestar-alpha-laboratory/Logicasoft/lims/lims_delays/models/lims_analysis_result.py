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
from odoo import fields, models
from odoo.addons.lims_delays.tools.delay_utils import convert_time_to_seconds


class LimsAnalysisResult(models.AbstractModel):
    _inherit = 'lims.analysis.result'

    technical_lead_date = fields.Datetime(string='Technical lead date', copy=False)
    technical_lead_time = fields.Float('Technical lead time', copy=False)
    is_technical_out_of_time = fields.Boolean('Technical out of time', copy=False)
    technical_warning_date = fields.Datetime(string='Technical warning date', copy=False)
    technical_warning_time = fields.Float('Technical warning time', copy=False)

    def add_parameter_values(self, method_param_charac_id, vals):
        vals = super().add_parameter_values(method_param_charac_id, vals)
        vals.update(self.get_delays(method_param_charac_id))
        return vals

    def get_delays(self, method_param_charac_id=False):
        if not method_param_charac_id:
            method_param_charac_id = self.method_param_charac_id
        return {
            'technical_lead_time': method_param_charac_id.technical_lead_time,
            'technical_warning_time': method_param_charac_id.technical_warning_time,
        }

    def check_out_of_time(self, date_for_compute, ending_date=False):
        """
        Set out of time of result (if needed)
        :param date_for_compute: datetime field from analysis, that causes the count of delay to begin
        :param ending_date: facultative attribute in case some other ending_date than standard behavior must be set
        :return: None
        """
        # results can be numeric, selection, compute or text (but in recordset they'll always be the same type)
        in_result_ids = out_result_ids = self.env[self._name]
        for result_id in self.filtered(lambda s: s.technical_lead_time > 0):
            beginning_date = result_id.analysis_id.read([date_for_compute])[0].get(date_for_compute)
            if not beginning_date:
                continue
            if not ending_date:
                end_date = result_id.date_start or fields.Datetime.now()
            else:
                end_date = ending_date
            lead_time_second = convert_time_to_seconds(result_id.technical_lead_time)
            alert_time_second = convert_time_to_seconds(result_id.technical_warning_time)
            technical_lead_date = beginning_date + lead_time_second
            if not result_id.technical_lead_date or result_id.technical_lead_date != technical_lead_date:
                result_id.write({
                    'technical_lead_date': technical_lead_date,
                    'technical_warning_date': technical_lead_date - alert_time_second
                })
            if not result_id.is_technical_out_of_time and result_id.technical_lead_date < end_date:
                out_result_ids += result_id
            elif result_id.is_technical_out_of_time and result_id.technical_lead_date >= end_date:
                in_result_ids += result_id
        in_result_ids.write({
            'is_technical_out_of_time': False
        })
        out_result_ids.write({
            'is_technical_out_of_time': True
        })
