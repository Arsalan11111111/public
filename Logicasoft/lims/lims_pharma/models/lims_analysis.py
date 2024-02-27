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
from odoo import fields, models, api, exceptions, _


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    def get_unquantifiable_text(self):
        return self.env['ir.config_parameter'].sudo().get_param('unquantifiable_text', _("ND"))

    def get_value_of_result_id(self, result_id):
        res = super(LimsAnalysis, self).get_value_of_result_id(result_id)
        if 'is_unquantifiable' in result_id._fields:
            res.update({
                'is_unquantifiable': result_id.is_unquantifiable
            })
        if result_id._name in ['lims.analysis.numeric.result', 'lims.analysis.compute.result']:
            corrected_value = result_id.corrected_value if 'corrected_value' in result_id._fields else result_id.value
            if ('lod' in result_id._fields) and result_id.lod and (corrected_value <= result_id.lod):
                unquantifiable_text = self.get_unquantifiable_text()
                res.update({
                    'value_lt_lod': "< {} (LOD) ({})".format(result_id.lod, unquantifiable_text)
                })
            if ('loq' in result_id._fields) and result_id.loq and (corrected_value <= result_id.loq):
                res.update({
                    'value_lt_loq': "< {} (LOQ)".format(result_id.loq)
                })
        return res
