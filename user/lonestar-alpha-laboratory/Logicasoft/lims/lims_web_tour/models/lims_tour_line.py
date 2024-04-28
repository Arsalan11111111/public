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
from odoo import models, fields


class LimsTourLine(models.Model):
    _inherit = 'lims.tour.line'

    color = fields.Selection([('orange', 'Orange'), ('green', 'Green'), ('black', 'Black')], compute='compute_color')

    def compute_color(self):
        done_stage_id = self.env['lims.result.stage'].search([('type', '=', 'done')])
        for record in self.filtered(lambda r: r.analysis_id):
            record.color = 'black'
            if record.analysis_id:
                result_num_ids = record.analysis_id.result_num_ids.filtered(
                    lambda r: r.method_param_charac_id.on_web)
                result_sel_ids = record.analysis_id.result_sel_ids.filtered(
                    lambda r: r.method_param_charac_id.on_web)
                result_text_ids = record.analysis_id.result_text_ids.filtered(
                    lambda r: r.method_param_charac_id.on_web)

                if (result_num_ids and any(result.stage_id == done_stage_id for result in result_num_ids)) or \
                        (result_sel_ids and any(result.stage_id == done_stage_id for result in result_sel_ids)) or (
                        (result_text_ids and any(result.stage_id == done_stage_id for result in result_text_ids))
                ):
                    record.color = 'orange'

                if result_num_ids:
                    if result_sel_ids:
                        if result_text_ids:
                            if all(result.stage_id == done_stage_id for result in result_num_ids) and \
                                    all(result.stage_id == done_stage_id for result in result_sel_ids) and all(
                                result.stage_id == done_stage_id for result in result_text_ids
                            ):
                                record.color = 'green'

                        elif all(result.stage_id == done_stage_id for result in result_num_ids) and \
                                all(result.stage_id == done_stage_id for result in result_sel_ids):
                            record.color = 'green'
                    else:
                        if all(result.stage_id == done_stage_id for result in result_num_ids):
                            record.color = 'green'
                else:
                    if result_sel_ids:
                        if result_text_ids:
                            if all(result.stage_id == done_stage_id for result in result_sel_ids) and all(
                                    result.stage_id == done_stage_id for result in result_text_ids):
                                record.color = 'green'
                        elif all(result.stage_id == done_stage_id for result in result_sel_ids):
                            record.color = 'green'
                    elif result_text_ids and all(result.stage_id == done_stage_id for result in result_text_ids):
                        record.color = 'green'
