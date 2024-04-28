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
from odoo import api, models, _


class LimsAnalysisReportReportParser(models.AbstractModel):
    _inherit = 'report.lims_report.analysis_report_qweb'

    def get_all_inta_accreditations(self, doc):
        all_analysis = doc.report_analysis_line_ids.analysis_id
        accreditations = []
        all_groups = all_analysis.get_parameter_print_group()
        for analysis in all_analysis:
            for print_section in analysis.get_report_section_ids(all_groups):
                for print_group in analysis.get_parameter_print_group_section(all_groups, print_section):
                    if self.check_if_result(analysis, print_group):
                        for parameter_print in print_group.parameter_print_ids:
                            result = analysis.get_result_vals(parameter_print)
                            if result and result['print_on_report'] and result.get('accreditation') and result['accreditation'] == 'inta':
                                self.set_accreditation(accreditations, result)
        return accreditations

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data=data)
        res.update({
            'get_all_inta_accreditations': self.get_all_inta_accreditations,
            'from_lon_report': True
        })
        return res
