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
from odoo import fields, models, api, _, exceptions


class LimsAnalysisComputeResult(models.Model):
    _inherit = 'lims.analysis.compute.result'

    plausible = fields.Boolean('NPL')

    def check_result_conformity(self):
        res = super(LimsAnalysisComputeResult, self).check_result_conformity()
        digits = self.env.ref('lims_base.analysis_result')
        for record in self.filtered(lambda r: r.limit_compute_result_ids.filtered(lambda l: l.type_alert == 'plausibility')):
            value = record.value
            plausible = True
            if value:
                for limit in record.limit_compute_result_ids.filtered(lambda l: l.type_alert == 'plausibility'):
                    operator_from = limit.operator_from
                    if operator_from == '=':
                        operator_from = '=='
                    elif operator_from == '<>':
                        operator_from = '!='
                    if limit.operator_to:
                        operator_to = limit.operator_to
                        if operator_to == '=':
                            operator_to = '=='
                        elif operator_to == '<>':
                            operator_to = '!='
                        formula = '%s %s %s and %s %s %s' % (
                        round(value, digits.digits), operator_from, round(limit.limit_value_from, digits.digits),
                        round(value, digits.digits), operator_to, round(limit.limit_value_to, digits.digits))
                    else:
                        formula = '%s %s %s' % (
                        round(value, digits.digits), operator_from, round(limit.limit_value_from, digits.digits))
                    try:
                        if eval(formula):
                            plausible = False
                            break
                    except ValueError:
                        raise exceptions.ValidationError(_('Parameter is not correctly configured.'))
                record.plausible = plausible
        return res
