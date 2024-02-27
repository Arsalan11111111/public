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
from odoo import models, api


class LimsParameterPack(models.Model):
    _inherit = 'lims.parameter.pack'

    def write(self, vals):
        if vals.get('parameter_ids'):
            tour_line_model_ids = self.env['lims.tour'].search([('is_model', '=', True)]).mapped('tour_line_ids')
            add_parameters_obj = self.env['add.parameters.wizard']
            param_obj = self.env['lims.method.parameter.characteristic']
            if tour_line_model_ids:
                for parameter_id in vals.get('parameter_ids'):
                    if parameter_id[0] == 0:
                        method_param = param_obj.browse(parameter_id[2].get('method_param_charac_id'))
                        tour_line_model_ids = tour_line_model_ids.filtered(
                            lambda t: t.pack_ids and any(pack in self for pack in t.pack_ids))
                        if tour_line_model_ids:
                            analysis_ids = tour_line_model_ids.mapped('analysis_id')
                            for analysis_id in analysis_ids:
                                add_parameters_id = add_parameters_obj.create({'analysis_id': analysis_id.id})
                                add_parameters_id.method_param_charac_ids = method_param
                                add_parameters_id.onchange_parameter_characteristic_id()
                                add_parameters_id.create_results()
                            result = self.get_result(analysis_ids, method_param)
                            if result:
                                result.write({'pack_id': parameter_id[2].get('pack_id')})
                    elif parameter_id[0] == 2:
                        tour_line_model_ids = tour_line_model_ids.filtered(
                            lambda t: t.pack_ids and any(pack in self for pack in t.pack_ids))
                        if tour_line_model_ids:
                            analysis_ids = tour_line_model_ids.mapped('analysis_id')
                            pack_line = self.env['lims.parameter.pack.line'].browse(parameter_id[1])
                            method_param = pack_line.method_param_charac_id
                            result = self.get_result(analysis_ids, method_param)
                            if result:
                                result.unlink()
        return super(LimsParameterPack, self).write(vals)

    def get_result(self, analysis_ids, method_param):
        result = analysis_ids.mapped('result_num_ids').filtered(
            lambda r: r.method_param_charac_id == method_param)
        if not result:
            result = analysis_ids.mapped('result_sel_ids').filtered(
                lambda r: r.method_param_charac_id == method_param)
        if not result:
            result = analysis_ids.mapped('result_compute_ids').filtered(
                lambda r: r.method_param_charac_id == method_param)
        if not result:
            result = analysis_ids.mapped('result_text_ids').filtered(
                lambda r: r.method_param_charac_id == method_param)
        return result or False
