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


class LimsAnalysisResult(models.AbstractModel):
    _inherit = 'lims.analysis.result'

    rel_parameter_print = fields.Many2one(related='method_param_charac_id.parameter_print_id', store=True)
    report_limit_value = fields.Char(string="Limit value", translate=True,
                                     help='Text that will be printed on the report, if the print configuration '
                                          'is correctly configured.')
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        all_translations = {}
        for vals in vals_list:
            if (vals.get('report_limit_value') and isinstance(vals['report_limit_value'], dict) and
                    vals.get('analysis_id')):
                all_translations.update({
                    (vals['analysis_id'], vals['method_param_charac_id']): vals.get('report_limit_value')
                })
        if all_translations:
            for record in res:
                translations = all_translations.get((record.analysis_id.id, record.method_param_charac_id.id))
                record._update_field_translations('report_limit_value', translations)
        return res

    def add_parameter_values(self, method_param_charac_id, vals):
        res = super(LimsAnalysisResult, self).add_parameter_values(method_param_charac_id, vals)
        print_on_report = False
        if method_param_charac_id.parameter_print_id:
            print_on_report = method_param_charac_id.parameter_print_id.is_default_print_on_report
        res.update({
            'report_limit_value': self.with_context(analysis=vals.get('analysis_id')).get_report_limit_value(method_param_charac_id),
            'print_on_report': print_on_report,
        })
        return res

    def get_report_limit_value(self, method_param_charac_id):
        """
        Function needed to be surcharged (lims_product_limits, lims_partner_limit)
        :param method_param_charac_id:
        :param vals:
        :return:
        """
        return self.get_report_limit_value_from_parameter(method_param_charac_id)

    def get_report_limit_value_from_parameter(self, method_param_charac_id):
        """
        Function needed to be surcharged (lims_product_limits, lims_partner_limit)
        :param method_param_charac_id:
        :return:
        """
        return method_param_charac_id._fields.get('report_limit_value')._get_stored_translations(method_param_charac_id)

    def get_export_value_protection(self):
        return 'lock' if self.analysis_id.is_locked else 'unlock'
