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
from odoo import fields, api, models, exceptions, _
from statistics import mean


class ParameterPrintGroupParser(models.AbstractModel):
    _name = 'report.lims_report_column.parameter_print_group_qweb'
    _description = 'Parameter Print Group Parser'

    def check_if_result(self, analysis_id, print_group_ids):
        parameter_print_ids = print_group_ids.mapped('parameter_print_ids')
        for parameter_print_id in parameter_print_ids:
            result_vals = analysis_id.get_result_vals(parameter_print_id)
            if result_vals:
                return True
        return False

    def get_analysis(self, doc):
        return doc.report_analysis_line_ids.mapped('analysis_id')

    def get_parameter_print_group_ids(self, analysis_ids):
        parameter_print_group_ids = self.env['lims.parameter.print.group'].browse()
        for analysis_id in analysis_ids:
            for parameter_print_group_id in analysis_id.get_parameter_print_group():
                if parameter_print_group_id not in parameter_print_group_ids:
                    parameter_print_group_ids += parameter_print_group_id

        return parameter_print_group_ids

    def get_sop_ids(self, analysis_ids, parameter_print_group_id):
        return analysis_ids.filtered(lambda a: parameter_print_group_id in a.get_parameter_print_group()).\
            mapped('sop_ids')

    def no_empty_column(self, parameter_print_ids, sop_ids):
        return parameter_print_ids.filtered(lambda p: any([self.get_result_vals(sop_id, p) for sop_id in sop_ids]))

    def no_empty_line(self, parameter_print_ids, sop_ids):
        return sop_ids.filtered(lambda s: any([self.get_result_vals(s, parameter_print_id)
                                               for parameter_print_id in parameter_print_ids]))

    def get_results_from_sop(self, sop_id):
        all_results = []
        all_results += sop_id.result_num_ids.\
            filtered(lambda r: r.stage_id.type in ['done', 'validated'] and r.print_on_report)
        all_results += sop_id.result_sel_ids.\
            filtered(lambda r: r.stage_id.type in ['done', 'validated'] and r.print_on_report)
        all_results += sop_id.result_compute_ids.\
            filtered(lambda r: r.stage_id.type in ['done', 'validated'] and r.print_on_report)
        all_results += sop_id.result_text_ids.\
            filtered(lambda r: r.stage_id.type in ['done', 'validated'] and r.print_on_report)
        return all_results

    def get_result_vals(self, sop_id, parameter_print_id):
        all_results = self.get_results_from_sop(sop_id)
        for result in all_results:
            if result.rel_parameter_print == parameter_print_id:
                result_vals = result.analysis_id.get_value_of_result_id(result)
                return result_vals
        return False

    def display_average(self, parameter_print_ids):
        return True if parameter_print_ids.filtered('print_mean_report') else False

    def get_units(self, sop_ids, parameter_print_id):
        units = []
        for sop_id in sop_ids:
            result = self.get_result_vals(sop_id, parameter_print_id)
            if result:
                unit = result.get('uom')
                units.append(unit)

        return set(units)

    def get_mean(self, sop_ids, parameter_print_id, unit):
        if parameter_print_id.parameter_characteristic_ids and \
                parameter_print_id.parameter_characteristic_ids[0].format in ['nu', 'ca']:
            method_param_charac_id = parameter_print_id.parameter_characteristic_ids[0]
            precision = method_param_charac_id.nbr_dec_showed

            vals = []
            for sop_id in sop_ids:
                result = self.get_result_vals(sop_id, parameter_print_id)
                if result and (result.get('uom') == unit):
                    value = result.get('value')

                    lang = result.get('lang')
                    lang_id = self.env['res.lang'].search([('code', '=', lang)])
                    thousands_sep = lang_id.thousands_sep if lang_id else ','
                    decimal_point = lang_id.decimal_point if lang_id else '.'

                    if thousands_sep in value:
                        value = value.replace(thousands_sep, '')
                    if decimal_point in value:
                        value = value.replace(decimal_point, '.')
                    vals.append(float(value))

            return round(mean(vals), precision) if vals else ''

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': self.env['lims.analysis.report'].browse(docids),
            'doc_model': 'lims.analysis.report',
            'data': data,
            'check_if_result': self.check_if_result,
            'get_analysis': self.get_analysis,
            'get_parameter_print_group_ids': self.get_parameter_print_group_ids,
            'get_sop_ids': self.get_sop_ids,
            'no_empty_column': self.no_empty_column,
            'no_empty_line': self.no_empty_line,
            'get_result_vals': self.get_result_vals,
            'display_average': self.display_average,
            'get_units': self.get_units,
            'get_mean': self.get_mean,
        }
