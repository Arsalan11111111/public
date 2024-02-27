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
from odoo import fields, models


class LimsAnalysisNumericResult(models.Model):
    _inherit = 'lims.analysis.numeric.result'

    def get_export_values(self, ordered_dictionary=None):
        ordered_dictionary = super().get_export_values(ordered_dictionary)
        ordered_dictionary.update(
            {'dilution': {'value': self.dilution_factor or '',
                          'protection': 'unlock' if self.rel_change_result else 'lock',
                          'validate': {'type': 'decimal', 'operator': 'between', 'formula1': 0.00000001,
                                        'formula2': self.rel_laboratory_id.dilution_factor_max},
                                       },
             'lod': {'value': self.lod or ''},
             'loq': {'value': self.loq or ''},
             'mloq': {'value': self.mloq or ''}}
        )

        if self.rel_change_loq:
            numeric_unlock_format = {'protection': 'unlock',
                                     'validate': {'type': 'custom', 'formula1': '=ISNUMBER({})'}}

            ordered_dictionary['lod'].update(numeric_unlock_format)
            ordered_dictionary['loq'].update(numeric_unlock_format)
            ordered_dictionary['mloq'].update(numeric_unlock_format)
        return ordered_dictionary

    def get_export_value(self, dictionary=None):
        if not dictionary:
            dictionary = {}
        dictionary = {'value': 0.0 if self.is_null else self.value or ''}
        if self.rel_change_result:
            dictionary.update({'protection': 'unlock',
                               'validate': {'type': 'custom', 'formula1': '=ISNUMBER({})'}})
        return dictionary
