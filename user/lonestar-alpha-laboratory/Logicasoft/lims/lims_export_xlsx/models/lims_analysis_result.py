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
from collections import OrderedDict

from odoo import models


class LimsAnalysisResult(models.AbstractModel):
    _inherit = 'lims.analysis.result'

    def get_export_values(self, ordered_dictionary=None):
        if not ordered_dictionary:
            ordered_dictionary = OrderedDict()
        ordered_dictionary.update({
            'result_id': {'value': self.id or ''},
            'result_format': {'value': self.method_param_charac_id.format or ''},
            'request': {'value': (self.rel_request_id and self.rel_request_id.name) or ''},
            'analysis': {'value': (self.analysis_id and self.analysis_id.name) or ''},
            'test': {'value': (self.sop_id and self.sop_id.name) or ''},
            'parameter': {'value': (self.method_param_charac_id and self.method_param_charac_id.tech_name) or ''},
            'value': self.get_export_value(),
            'uom': {'value': (self.uom_id and self.uom_id.name) or '',
                    'validate': {"type": "list", "formula1": "_odoo_!_uom_names", "allow_blank": True},
                    'protection': self.get_export_value_protection() if self.rel_change_result else 'lock'
                    },
            'state': {'value': self.get_state_translated(self.state) or ''},
            'stage': {'value': (self.stage_id and self.stage_id.name) or ''},
            'comment': {'value': self.comment or '',
                        'protection': self.get_export_value_protection() if self.rel_change_result else 'lock'}
        })
        return ordered_dictionary

    def get_export_value_protection(self):
        """
        Context: analysis lock notion come from 'lims_report' module but with this function we avoid the dependence.
        :return:
        """
        return 'unlock'

    def get_export_value(self, dictionary=None):
        """
        Must be implemented in each result type.
        Format:

        :param dictionary:
        :return:
        """
        raise NotImplementedError()

    def _get_result_ids(self):
        """
        Context: this function is not used until custom security or a custom results filter or similar has been set up
        (you know that LIMS clients are able to ask for this).
        :return:
        """
        return self

    def update_dictonnary_mapper(self, collections):
        """
        Context: This dictonnary is used in set_fields_update_dictonnary(...) and _set_field_update_dictonnary(...)
        Format [('name from _get_header_list()', field in odoo if different from name, id convertor dictonnary)]
        Id convertor dictonnary it's for O2M Format only:
        Exemple : Excel file value = 'Toto' in Odoo O2M.name = Toto O2M.id = 4, field = tag_ids
                {'Toto':4}

        Typically, be integrated by collections .
        collections = {'tag_ids': {'Toto':4, 'Tata':6 ....}}
        :param collections:
        :return:
        """
        return [
            ('uom', 'uom_id', collections.get('uom_ids')),
            ('comment', None, None)
        ]

    def set_fields_update_dictonnary(self, result_dictionary, result_id, vals, collections):
        """
        Default function to put value in models.
        Can be surcharged in specific result_type. (see Nu or Se).
        :param result_dictionary:
        :param result_id:
        :param vals:
        :param collections:
        :return:
        """
        for element in self.update_dictonnary_mapper(collections):
            self._set_field_update_dictonnary(result_dictionary, result_id, vals, element[0] or None,
                                              element[1] or None, element[2] or None)

    def set_import_value(self, dictionary=None, collections=None):
        """
        Global loop to import (By type and By analysis)
        :param dictionary:
        :param collections:
        :return:
        """
        collections = collections or {}
        result_ids = self._get_result_ids()
        if result_ids and dictionary:
            for result_id in result_ids:
                vals = dictionary.get(result_id.id)
                result_dictionary = {}
                self.set_fields_update_dictonnary(result_dictionary, result_id, vals, collections)
                result_dictionary and result_id.write(result_dictionary)

    @staticmethod
    def _set_field_update_dictonnary(result_dictionary, result_id, vals, arg=None, field=None, o2m_ids=None):
        """
        Working core to determine if value must be updated in import.
        (Objective avoid to write in model if value field have the same value in Excel)
        :param result_dictionary:
        :param result_id:
        :param vals:
        :param arg:
        :param field:
        :param o2m_ids:
        :return:
        """
        if not field:
            field = arg
        # Get the id from a collection in file
        value = vals and vals.get(arg) and not vals.get(arg)[1] and vals.get(arg)
        result_value = result_id and result_id[field]
        if o2m_ids:
            if (value and not value[1] and
                    any([bool(value[0] and o2m_ids.get(value[0])), bool(result_value and result_value.id)]) and
                    o2m_ids.get(value[0]) != result_value.id):
                result_dictionary[field] = o2m_ids.get(value[0])
        # Get value from a cell in file
        elif value:
            if not value[1] and value[0] != result_value and any([bool(value[0]), bool(result_value)]):
                result_dictionary[field] = value[0]
