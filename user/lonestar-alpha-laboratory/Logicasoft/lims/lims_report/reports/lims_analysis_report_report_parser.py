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
    _name = 'report.lims_report.analysis_report_qweb'
    _inherit = 'report.lims_report.lims_analysis_base_report_parser'
    _description = 'Analysis Report Parser'

    def get_method_attribute(self, analysis_ids):
        sop_ids = analysis_ids.mapped('sop_ids').filtered(lambda s: s.rel_type != 'cancel')
        if sop_ids:
            return sop_ids.mapped('attribute_ids').filtered(lambda a: a.to_print)
        return False

    def check_if_result(self, analysis_id, print_group_ids):
        parameter_print_ids = print_group_ids.mapped('parameter_print_ids')
        for parameter_print_id in parameter_print_ids:
            result_vals = analysis_id.get_result_vals(parameter_print_id)
            if result_vals:
                return True
        return False

    def get_analysis(self, doc):
        return doc.report_analysis_line_ids.mapped('analysis_id')

    def check_if_comment(self, analysis_id):
        return bool(analysis_id.result_num_ids.filtered(lambda r: r.show and r.comment) or
                    analysis_id.result_sel_ids.filtered(lambda rs: rs.show and rs.comment) or
                    analysis_id.result_text_ids.filtered(lambda rt: rt.show and rt.comment) or
                    analysis_id.result_compute_ids.filtered(lambda rc: rc.show and rc.comment))

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        res.update({
            'check_if_result': self.check_if_result,
            'get_method_attribute': self.get_method_attribute,
            'get_analysis': self.get_analysis,
            'check_if_comment': self.check_if_comment,
        })
        return res
