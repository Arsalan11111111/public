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


class LimsLaboratory(models.Model):
    _inherit = 'lims.laboratory'

    default_commercial_lead_time = fields.Float(string='Default commercial lead time',
                                                help='if empty no default value will be used. Allows to have a '
                                                     'default value when creating a parameter pack, or changing the '
                                                     'laboratory in a parameter pack.')
    default_commercial_warning_time = fields.Float(string='Default commercial warning time',
                                                   help='if empty no default value will be used. Allows to have a '
                                                        'default value when creating a parameter pack, or changing '
                                                        'the laboratory in a parameter pack.')
    default_technical_lead_time = fields.Float(string='Default technical lead time',
                                               help='if empty no default value will be used. Allows to have a '
                                                    'default value when creating a parameter characteristic, or '
                                                    'changing the laboratory in a parameter characteristic.')
    default_technical_warning_time = fields.Float(string='Default technical warning time',
                                                  help='if empty no default value will be used. Allows to have a '
                                                       'default value when creating a parameter characteristic, or '
                                                       'changing the laboratory in a parameter characteristic.')

    date_for_compute_warning_time = fields.Selection([('sample', 'Date Sample'),
                                                      ('sample_receipt', 'Date Sample Receipt')])
    date_end_for_compute_warning_time = fields.Selection([
        ('analysis_start', 'Date Start Analysis'),
        ('analysis_end', 'Date End Analysis'),
        ('analysis_report', 'Date Report Analysis'),
        ('now', 'Actual Date'),
    ])
    delay_result_stage_ids = fields.Many2many('lims.result.stage', domain=[('type', 'in', ['todo', 'wip'])],
                                              help="Out of time calculation will be active for results within those "
                                                   "stages", string="Result stages used for delay")

    def get_date_begin_delays(self):
        """
        Return the field of lims.analysis that will be used for the beginning of delay calculation
        :return: a string that MUST BE the name of a datetime field on model lims.analysis
        """
        return 'date_sample'
