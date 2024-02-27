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


class LimsAnalysisSelResult(models.Model):
    _inherit = 'lims.analysis.sel.result'

    def get_export_value(self, dictionary=None):
        if not dictionary:
            dictionary = {}
        dictionary = {'value': (self.value_id and self.value_id.name) or ''}
        if self.rel_change_result:
            values = self.method_param_charac_id.parameter_id.result_value_ids.mapped('name')
            if values:
                defined_name = f'_se_value_ids_{self.method_param_charac_id.parameter_id.id}'
                formula1 = f'_odoo_!{defined_name}'
                dictionary.update({'validate': {'type': 'list',
                                                'defined_name': defined_name,
                                                'values': values,
                                                'formula1': formula1},
                                   'protection': 'unlock'})
        return dictionary
