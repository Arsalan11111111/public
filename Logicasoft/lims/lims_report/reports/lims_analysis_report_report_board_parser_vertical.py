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
from odoo import api, models


class LimsAnalysisReportReportBoardParserVertical(models.AbstractModel):
    _name = 'report.lims_report.analysis_report_board_vertical'
    _inherit = 'report.lims_report.lims_analysis_base_report_parser'
    _description = 'Analysis Report Board Parser (V)'

    def get_parameters(self, report_id):
        analysis_ids = report_id.report_analysis_line_ids.mapped('analysis_id')
        parameters = analysis_ids.mapped('result_num_ids').filtered(lambda r: r.print_on_report)\
                         .mapped('method_param_charac_id').mapped('parameter_print_id') + \
                     analysis_ids.mapped('result_sel_ids').filtered(lambda r: r.print_on_report)\
                         .mapped('method_param_charac_id').mapped('parameter_print_id') + \
                     analysis_ids.mapped('result_compute_ids').filtered(lambda r: r.print_on_report) \
                         .mapped('method_param_charac_id').mapped('parameter_print_id') + \
                     analysis_ids.mapped('result_text_ids').filtered(lambda r: r.print_on_report) \
                         .mapped('method_param_charac_id').mapped('parameter_print_id')
        return set(parameters)

    def get_value(self, analysis_id, parameter_print):
        result = analysis_id.result_num_ids.filtered(
            lambda r: r.print_on_report and r.rel_parameter_print == parameter_print)
        if not result:
            result = analysis_id.result_sel_ids.filtered(
                lambda r: r.print_on_report and r.rel_parameter_print == parameter_print)
        if not result:
            result = analysis_id.result_compute_ids.filtered(
                lambda r: r.print_on_report and r.rel_parameter_print == parameter_print)
        if not result:
            result = analysis_id.result_text_ids.filtered(
                lambda r: r.print_on_report and r.rel_parameter_print == parameter_print)
        if len(result) == 1:
            values = analysis_id.get_value_of_result_id(result)
            return values
        return ''

    def set_all_board(self, report_id):
        parameter_ids = self.get_parameters(report_id)
        all_board = []
        board = []
        for parameter_id in parameter_ids:
            board.append(parameter_id)
            if len(board) == 3 or len(board) == 4:
                all_board.append(board.copy())
                board = []
        if board:
            all_board.append(board.copy())
        return all_board

    def set_accreditation_type(self, accreditation_type, accreditation):
        accreditation_type.append(accreditation)
        return accreditation_type

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super()._get_report_values(docids, data)
        res.update({
            'set_all_board': self.set_all_board,
            'get_value': self.get_value,
            'data': data,
            'set_accreditation_type': self.set_accreditation_type,
        })
        return res
