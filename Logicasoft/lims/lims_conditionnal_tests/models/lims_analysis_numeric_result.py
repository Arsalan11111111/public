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


class LimsAnalysisNumericResult(models.Model):
    _inherit = 'lims.analysis.numeric.result'

    def get_limit_vals(self, limit):
        res = super(LimsAnalysisNumericResult, self).get_limit_vals(limit)
        if limit.pack_ids:
            res.update({
                'pack_ids': [(4, pack.id) for pack in limit.pack_ids]
            })
        return res

    def check_result_conformity(self):
        parameter_obj = self.env['lims.method.parameter.characteristic']
        res = super(LimsAnalysisNumericResult, self).check_result_conformity()
        for record in self:
            limit_id = record.get_result_limit(record.corrected_value)
            if limit_id and limit_id.pack_ids:
                record.analysis_id.add_parameters_and_packs(pack_ids=limit_id.pack_ids, param_ids=parameter_obj)
        return res
