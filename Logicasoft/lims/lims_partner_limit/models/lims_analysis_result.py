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
from odoo import models


class LimsAnalysisResult(models.AbstractModel):
    _inherit = 'lims.analysis.result'

    def get_limits_from_partner(self):
        partner = self.analysis_id.partner_id
        if partner:
            param_char_partner_ids = self.method_param_charac_id.param_partner_ids.filtered(
                lambda p: p.partner_id == partner
            )
            if param_char_partner_ids:
                return param_char_partner_ids[-1].limit_ids

    def get_limit_result_ids(self):
        """
        Return limit from the partner

        :return:
        """
        limits = self.get_limits_from_partner()
        if limits:
            return limits
        return super().get_limit_result_ids()

    def get_report_limit_value(self, method_param_charac_id, vals=None):
        """
        Get the report_limit_value if exist in partner limit, else get from the parameter

        :param method_param_charac_id:
        :param vals:
        :return:
        """
        vals = vals or {}
        analysis = self.analysis_id or self.env['lims.analysis'].browse(vals.get('analysis_id', False))
        report_limit_value = False
        if analysis and analysis.partner_id:
            report_limit_value = self.get_report_limit_value_from_partner(method_param_charac_id, analysis, vals)

        return report_limit_value if report_limit_value else super().get_report_limit_value(method_param_charac_id)

    def get_report_limit_value_from_partner(self, method_param_charac_id, analysis, vals=None):
        """
        Find the report limit value to set in parameter's partners information.

        :param method_param_charac_id:
        :param analysis:
        :param vals:
        :return:
        """
        vals = vals or {}
        if analysis.partner_id in method_param_charac_id.param_partner_ids.partner_id:
            report_limit_value = method_param_charac_id.param_partner_ids.filtered(
                lambda p: p.partner_id == analysis.partner_id)[0].report_limit_value
            return report_limit_value

    def get_result_vals(self):
        res = super().get_result_vals()
        report_limit_value = self.get_report_limit_value_from_partner(self.method_param_charac_id, self.analysis_id)
        if report_limit_value:
            res.update({
                'report_limit_value': report_limit_value,
            })
        return res
