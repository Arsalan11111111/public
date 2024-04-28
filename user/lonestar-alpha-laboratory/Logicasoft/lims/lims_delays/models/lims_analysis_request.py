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
from datetime import datetime


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    commercial_lead_date = fields.Datetime(string='Commercial lead date',
                                           help='If one of these analysis are not completed on time, it will be '
                                                'marked as \'out of time\'. this date is calculated from the analysis '
                                                'which has the longest commercial lead time.',
                                           copy=False,
                                           compute='get_analysis_request_time',
                                           store=True, tracking=True)
    commercial_warning_date = fields.Datetime(string='Commercial warning date',
                                              help='If one of these analysis are not completed before the warning '
                                                   'date, it will be marked as \'warning time\'. this date is '
                                                   'calculated with the warning time from the analysis which has the '
                                                   'longest commercial lead time.',
                                              copy=False,
                                              compute='get_analysis_request_time',
                                              store=True)
    is_commercial_out_of_time = fields.Boolean('Commercial out of time', compute='get_analysis_request_time',
                                               help='Mark this request as \' commercially out of time\'.',
                                               store=True)

    @api.depends('analysis_ids', 'analysis_ids.stage_id', 'analysis_ids.date_sample_receipt',
                 'analysis_ids.commercial_lead_date')
    def get_analysis_request_time(self):
        """
        Get all the commercials dates from the analysis with the highest 'commercial_lead_date'
        only on request with the state : 'accepted or in_progress'
        :return:
        """
        for record in self:
            commercial_lead_date = False
            commercial_warning_date = False
            if record.analysis_ids:
                analysis = record.analysis_ids.filtered(
                    lambda a: a.commercial_lead_date and a.stage_id.type != 'cancel').sorted(
                    key=lambda a: a.commercial_lead_date)
                if analysis:
                    commercial_lead_date = analysis[0].commercial_lead_date
                    commercial_warning_date = analysis[0].commercial_warning_date
            record.commercial_lead_date = commercial_lead_date
            record.commercial_warning_date = commercial_warning_date
            is_commercial_out_of_time = record.is_commercial_out_of_time
            if record.state in ['accepted', 'in_progress'] and commercial_lead_date:
                if commercial_lead_date >= fields.Datetime.now():
                    is_commercial_out_of_time = False
                else:
                    is_commercial_out_of_time = True
            record.is_commercial_out_of_time = is_commercial_out_of_time
