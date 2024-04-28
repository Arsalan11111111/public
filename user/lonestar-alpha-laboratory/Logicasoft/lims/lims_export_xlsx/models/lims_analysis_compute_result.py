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


class LimsAnalysisComputeResult(models.Model):
    _inherit = 'lims.analysis.compute.result'

    def get_export_values(self, ordered_dictionary=None):
        ordered_dictionary = super().get_export_values(ordered_dictionary)
        ordered_dictionary.update(
            {'lod': {'value': self.lod or ''},
             'loq': {'value': self.loq or ''},
             'mloq': {'value': self.mloq or ''}})
        if self.rel_change_loq:
            numeric_unlock_format = {'protection': self.get_export_value_protection(),
                                     'validate': {'type': 'custom', 'formula1': '=ISNUMBER({})'}}
            ordered_dictionary['lod'].update(numeric_unlock_format)
            ordered_dictionary['loq'].update(numeric_unlock_format)
            ordered_dictionary['mloq'].update(numeric_unlock_format)
        return ordered_dictionary

    def get_export_value(self, dictionary=None):
        if not dictionary:
            dictionary = {'value': self.value}
        return dictionary

    def update_dictonnary_mapper(self, collections):
        mapper = super().update_dictonnary_mapper(collections)
        mapper.extend([
            ('lod', None, None),
            ('loq', None, None),
            ('mloq', None, None),
        ])
        return mapper
