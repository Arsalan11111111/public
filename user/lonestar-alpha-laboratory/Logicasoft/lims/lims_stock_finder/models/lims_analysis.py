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
from odoo import models, api, exceptions, _, fields
from odoo.tools.convert import safe_eval


def eval_criteria(criteria):
    result = False
    try:
        safe_eval(criteria)
        result = True
    finally:
        return result


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    @staticmethod
    def get_default_search_domain():
        return [('rel_type', '=', 'validated2')]

    def filter_analysis_with_criteria(self, analysis_ids=False, domain=False, criteria_ids=False):
        if not domain:
            domain = self.get_default_search_domain()
        if not analysis_ids:
            analysis_ids = self.env['lims.analysis'].search(domain)
        criteria_ids = self._filter_valid_criteria(criteria_ids)
        analysis_ids = self._find_minimal_analysis(analysis_ids, criteria_ids)
        if criteria_ids:
            for criteria_id in criteria_ids:
                results = self._find_results(criteria_id)
                analysis_ids = self._filter_analysis_list(analysis_ids, results.analysis_id)
                if not analysis_ids:
                    raise exceptions.UserError(
                        _('No analysis found with all criteria! Last criteria tested : [{}] with value [{}]').format(
                            criteria_id.parameter_id.name, criteria_id.criteria or criteria_id.state))
        return analysis_ids

    def _find_minimal_analysis(self, analysis_ids, criteria_ids):
        if len(analysis_ids) > 100 and criteria_ids and len(criteria_ids):
            results = self._find_results(criteria_ids[0])
            results_analysis_ids = results.analysis_id
            if len(results_analysis_ids) < len(analysis_ids):
                analysis_ids = results_analysis_ids
        return analysis_ids

    def _filter_valid_criteria(self, criteria_ids):
        criteria_ids = criteria_ids.filtered(lambda c: c.criteria_evaluated and eval_criteria(c.criteria_evaluated))
        return criteria_ids

    @staticmethod
    def _find_results(criteria_id):
        return criteria_id.parameter_id.result_search(safe_eval(criteria_id.criteria_evaluated))

    def _filter_analysis_list(self, analysis_list, analysis_ids):
        updated_analysis_list = self.env['lims.analysis']
        for analysis in analysis_list:
            if analysis.id in analysis_ids.ids:
                updated_analysis_list += analysis
        return updated_analysis_list

