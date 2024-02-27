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
from odoo import fields, models, api


class LimsAnalysisComputeResult(models.Model):
    _inherit = 'lims.analysis.compute.result'

    def get_limit_result_ids(self):
        if self.analysis_id.partner_id in self.method_param_charac_id.param_partner_ids.mapped('partner_id') and \
                        self.analysis_id.sampling_point_id in self.method_param_charac_id.param_partner_ids.mapped('sampling_point_id'):
            return self.method_param_charac_id.param_partner_ids.filtered(lambda p: p.partner_id == self.analysis_id.partner_id and
                                                                                    p.sampling_point_id == self.analysis_id.sampling_point_id).limit_ids

        if self.analysis_id.partner_id in self.method_param_charac_id.param_partner_ids.mapped('partner_id').filtered(lambda p: not p.sampling_point_id):
            return self.method_param_charac_id.param_partner_ids.filtered(lambda p: p.partner_id == self.analysis_id.partner_id and
                                                                                    not p.sampling_point_id).limit_ids

        if self.analysis_id.sampling_point_id in self.method_param_charac_id.param_partner_ids.mapped('sampling_point_id').filtered(lambda p: not p.partner_id):
            return self.method_param_charac_id.param_partner_ids.filtered(lambda p: p.sampling_point_id == self.analysis_id.sampling_point_id and
                                                                                    not p.partner_id).limit_ids
        return super(LimsAnalysisComputeResult, self).get_limit_result_ids()
