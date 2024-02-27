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
            'result': {'value': f'{self.method_param_charac_id.format}_{self.id}' or ''},
            'request': {'value': (self.rel_request_id and self.rel_request_id.name) or ''},
            'analysis': {'value': (self.analysis_id and self.analysis_id.name) or ''},
            'test': {'value': (self.sop_id and self.sop_id.name) or ''},
            'parameter': {'value': (self.method_param_charac_id and self.method_param_charac_id.tech_name) or ''},
            'value': self.get_export_value(),
            'uom': {'value': (self.uom_id and self.uom_id.name) or '',
                    'validate': {"type": "list", "formula1": "_odoo_!_uom_names", "allow_blank": True},
                    'protection': 'unlock' if self.rel_change_result else 'lock'
                    },
            'state': {'value': self.get_state_translated(self.state) or ''},
            'stage': {'value': (self.stage_id and self.stage_id.name) or ''},
            'comment': {'value': self.comment or '',
                        'protection': 'unlock' if self.rel_change_result else 'lock'}
        })
        return ordered_dictionary
