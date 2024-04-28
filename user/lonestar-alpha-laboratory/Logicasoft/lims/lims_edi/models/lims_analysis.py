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


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    def get_result_from_parameter(self, method_param_charac_id):
        if method_param_charac_id.format == 'nu' and self.result_num_ids:
            return self.result_num_ids.filtered(
                lambda r:
                r.method_param_charac_id.id == method_param_charac_id.id and r.rel_type not in ['cancel', 'rework'])
        elif method_param_charac_id.format == 'se' and self.result_sel_ids:
            return self.result_sel_ids.filtered(
                lambda r:
                r.method_param_charac_id.id == method_param_charac_id.id and r.rel_type not in ['cancel', 'rework'])
        elif method_param_charac_id.format == 'ca' and self.result_compute_ids:
            return self.result_compute_ids.filtered(
                lambda r:
                r.method_param_charac_id.id == method_param_charac_id.id and r.rel_type not in ['cancel', 'rework'])
        elif method_param_charac_id.format == 'tx' and self.result_text_ids:
            return self.result_text_ids.filtered(
                lambda r:
                r.method_param_charac_id.id == method_param_charac_id.id and r.rel_type not in ['cancel', 'rework'])
        return False

    def create_result(self, parameter_id, draft_stage_id, result_table=''):
        self.ensure_one()
        result_vals = {
            'method_param_charac_id': parameter_id.id,
            'analysis_id': self.id,
        }
        sop_id = self.sop_ids.filtered(lambda s: s.method_id == parameter_id.method_id and s.rel_type != 'cancel')
        if sop_id:
            result_vals.update({
                'sop_id': sop_id.id,
            })
        if not sop_id or sop_id.rel_type == 'draft':
            result_vals.update({
                'stage_id': draft_stage_id.id,
            })
        if not result_table:
            result_table = parameter_id.get_result_table()
        result_id = self.env[result_table].create(result_vals)
        if not sop_id:
            self.create_sop()
        if result_id.sop_id.rel_type == 'plan':
            result_id.do_plan()
        else:
            result_id.do_todo()
        return result_id
