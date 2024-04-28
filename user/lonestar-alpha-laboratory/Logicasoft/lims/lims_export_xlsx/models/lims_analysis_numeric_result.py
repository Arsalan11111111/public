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

    def get_export_values(self, ordered_dictionary=None):
        ordered_dictionary = super().get_export_values(ordered_dictionary)
        ordered_dictionary.update(
            {'dilution': {'value': self.dilution_factor or '',
                          'protection': self.get_export_value_protection() if self.rel_change_result else 'lock',
                          'validate': {'type': 'decimal', 'operator': 'between', 'formula1': 0.00000001,
                                       'formula2': self.rel_laboratory_id.dilution_factor_max},
                          },
             'lod': {'value': self.lod or ''},
             'loq': {'value': self.loq or ''},
             'mloq': {'value': self.mloq or ''}}
        )

        if self.rel_change_loq:
            numeric_unlock_format = {'protection': self.get_export_value_protection(),
                                     'validate': {'type': 'custom', 'formula1': '=ISNUMBER({})'}}

            ordered_dictionary['lod'].update(numeric_unlock_format)
            ordered_dictionary['loq'].update(numeric_unlock_format)
            ordered_dictionary['mloq'].update(numeric_unlock_format)
        return ordered_dictionary

    def get_export_value(self, dictionary=None):
        if not dictionary:
            dictionary = {'value': 0.0 if self.is_null else self.value or ''}
        if self.rel_change_result:
            dictionary.update({'protection': self.get_export_value_protection(),
                               'validate': {'type': 'custom', 'formula1': '=ISNUMBER({})'}})
        return dictionary

    def update_dictonnary_mapper(self, collections):
        mapper = super().update_dictonnary_mapper(collections)
        mapper.extend([
            ('dilution', 'dilution_factor', None),
            ('lod', None, None),
            ('loq', None, None),
            ('mloq', None, None),
        ])
        return mapper

    def set_fields_update_dictonnary(self, result_dictionary, result_id, vals, collections):
        self._set_value_update_dictonnary(result_dictionary, result_id, vals)
        super().set_fields_update_dictonnary(result_dictionary, result_id, vals, collections)

    @staticmethod
    def _set_value_update_dictonnary(result_dictionary, result_id, vals):
        """
        Context in Excel user cn set empty cell.
        Empty cell != cell with 0.0 or 0
        So we need to catch None value from cell to set result_id.value = 0 and result_id.is_null = False
        And also we need to catch 0 from a cell to set result_id.value = 0 and result_id.is_null = True
        :param result_dictionary:
        :param result_id:
        :param vals:
        :return:
        """
        if not vals or not vals.get('value') or vals.get('value')[1] or not result_id:
            return
        value = vals.get('value')[0]
        if not result_id.value and result_id.is_null:
            result_value = False
        elif not result_id.value:
            result_value = None
        else:
            result_value = result_id.value
        if result_value != value:
            result_dictionary['value'] = 0.0
            is_null = False
            if value is None or value:
                result_dictionary['value'] = value or 0.0
            else:
                is_null = True
            if any([result_id.is_null, is_null]):
                result_dictionary['is_null'] = is_null
