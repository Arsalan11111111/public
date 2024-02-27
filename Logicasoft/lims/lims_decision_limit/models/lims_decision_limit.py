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
import json


class LimsParameterLimit(models.Model):
    _name = 'lims.decision.limit'
    _description = 'Decision limit'
    _order = 'write_date desc, id desc'

    analysis_id = fields.Many2one('lims.analysis')
    collection_ids = fields.Many2many('lims.parameter.limit.collection', string='Collections tested')
    conform_collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                              string='Conform Collections',
                                              relation='lims_collection_conform_lims_decision_rel')
    non_conform_collection_ids = fields.Many2many('lims.parameter.limit.collection',
                                                  string='Non Conform Collections',
                                                  relation='lims_collection_non_conform_lims_decision_rel')
    set_ids = fields.Many2many('lims.parameter.limit.set')
    datas = fields.Text()

    def name_get(self):
        result = []
        for record in self:
            analysis = record.analysis_id.name if record.analysis_id else _('N/A')
            display_name = f"{analysis}: {record.write_date}"
            result.append((record.id, display_name))
        return result

    def get_data_json(self):
        return json.loads(self.datas)


