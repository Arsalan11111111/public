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
from odoo import models, exceptions, _
from datetime import date


class AnalysisXLSX(models.AbstractModel):
    _name = 'report.lims_report_xls.report_analysis_xlsx'
    _description = 'Report Lims_report_xls Report_analysis_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, analysis_ids):
        self = self.sudo()
        sheet = workbook.add_worksheet(date.today().isoformat())
        format = workbook.add_format()
        format.set_text_wrap()

        if not analysis_ids:
            raise exceptions.ValidationError(_('No analysis selected'))

        tb_param_charac_id_ids = {}

        col_number = 0
        titles = self.get_titles(analysis_ids[0])

        start_col_number = len(titles)
        for analysis_id in analysis_ids:
            # get method_param in result
            for result_id in analysis_id.result_num_ids:
                if not tb_param_charac_id_ids.get(result_id.method_param_charac_id.id):
                    tb_param_charac_id_ids.update(
                        {result_id.method_param_charac_id.id: result_id.method_param_charac_id})

            # get method_param in sel result
            for result_id in analysis_id.result_sel_ids:
                if not tb_param_charac_id_ids.get(result_id.method_param_charac_id.id):
                    tb_param_charac_id_ids.update(
                        {result_id.method_param_charac_id.id: result_id.method_param_charac_id})

            # get method_param in compute result
            for result_id in analysis_id.result_compute_ids:
                if not tb_param_charac_id_ids.get(result_id.method_param_charac_id.id):
                    tb_param_charac_id_ids.update(
                        {result_id.method_param_charac_id.id: result_id.method_param_charac_id})

            # get method_param in text result
            for result_id in analysis_id.result_text_ids:
                if not tb_param_charac_id_ids.get(result_id.method_param_charac_id.id):
                    tb_param_charac_id_ids.update(
                        {result_id.method_param_charac_id.id: result_id.method_param_charac_id})

        for param_charac_id in tb_param_charac_id_ids.values():
            sheet.write(0, col_number + start_col_number, param_charac_id.name or '', format)
            sheet.write(1, col_number + start_col_number, param_charac_id.uom.name or '', format)
            col_number += 1

        col_number = 0

        while col_number < len(titles):
            sheet.write(1, col_number, titles[col_number], format)
            col_number += 1

        row_number = 2
        for analysis_id in analysis_ids:
            data_analysis = self.get_data_analysis(analysis_id)
            col_number = 0
            while col_number < len(titles):
                if 'date' in data_analysis[col_number][2]:
                    format.set_num_format("dd/mm/yy")
                else:
                    format.set_text_wrap()

                sheet.write(row_number, col_number,
                            data_analysis[col_number][1], format)
                col_number += 1

            col_number = 0
            for parameter_id in tb_param_charac_id_ids:
                analysis_result_ids = self.get_search_analysis_result(analysis_id, parameter_id)
                val = ''
                analysis_result_id = analysis_result_ids.filtered(
                    lambda result: result.rel_type in ['done', 'validated'])
                if 'value_id' in analysis_result_id._fields:
                    val = analysis_result_id.value_id.name if analysis_result_id.value_id else ''
                elif 'corrected_value' in analysis_result_id._fields:
                    val = analysis_result_id.corrected_value
                    if 'is_null' in analysis_result_id._fields and analysis_result_id.is_null:
                        val = 0.0
                elif 'value' in analysis_result_id._fields:
                    val = analysis_result_id.value
                if val:
                    sheet.write(row_number, col_number + start_col_number, val, format.set_text_wrap())
                col_number += 1
            row_number += 1

    def get_data_analysis(self, analysis_id):
        # Collection of List : [[Title, Value, Format], ...[] ]
        data_analysis = [
            [(_('Request')), analysis_id.request_id.name if analysis_id.request_id else '', 'text'],
            [(_('Customer')), analysis_id.partner_id.name if analysis_id.partner_id else '', 'text'],
            [(_('Analysis')), analysis_id.name, 'text'],
            [(_('Matrix')), analysis_id.matrix_id.name if analysis_id.matrix_id else '', 'text'],
            [(_('Regulation')), analysis_id.regulation_id.name if analysis_id.regulation_id else '', 'text'],
            [(_('Reason')), analysis_id.reason_id.name if analysis_id.reason_id else '', 'text'],
            [(_('State')), analysis_id.state if analysis_id.state else '', 'text'],
            [(_('Stage')), analysis_id.stage_id.name if analysis_id.stage_id else '', 'text'],
            [(_('Date start')), analysis_id.date_start if analysis_id.date_start else '', 'date'],
            [(_('Due date')), analysis_id.due_date if analysis_id.due_date else '', 'date'],
            [(_('Date plan')), analysis_id.date_plan if analysis_id.date_plan else '', 'date']
        ]
        return data_analysis

    def get_titles(self, analysis_id):
        data_analysis = self.get_data_analysis(analysis_id)
        titles = [item[0] for item in data_analysis]
        return titles

    def get_search_analysis_result(self, analysis_id, parameter_id):
        analysis_result_id = self.env['lims.analysis.numeric.result'].search(
            [('analysis_id', '=', analysis_id.id), ('method_param_charac_id', '=', parameter_id)])
        if not analysis_result_id:
            analysis_result_id = self.env['lims.analysis.sel.result'].search(
                [('analysis_id', '=', analysis_id.id), ('method_param_charac_id', '=', parameter_id)])
        if not analysis_result_id:
            analysis_result_id = self.env['lims.analysis.compute.result'].search(
                [('analysis_id', '=', analysis_id.id), ('method_param_charac_id', '=', parameter_id)])
        if not analysis_result_id:
            analysis_result_id = self.env['lims.analysis.text.result'].search(
                [('analysis_id', '=', analysis_id.id), ('method_param_charac_id', '=', parameter_id)])
        return analysis_result_id
