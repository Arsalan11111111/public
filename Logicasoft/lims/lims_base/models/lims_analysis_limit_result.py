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
from odoo import fields, models, _


class LimsAnalysisLimitResult(models.AbstractModel):
    _name = 'lims.analysis.limit.result'
    _order = 'sequence, id'
    _description = 'Analysis Limit Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(default=1)
    limit_value_from = fields.Float('Limit Value From', digits='Analysis Result', tracking=True, required=True)
    limit_value_to = fields.Float('Limit Value To', digits='Analysis Result', tracking=True)
    operator_from = fields.Selection('get_operators', 'Operator From', tracking=True, required=True)
    operator_to = fields.Selection('get_operators', 'Operator To', tracking=True)
    type_alert = fields.Selection('get_type_alert_value', 'Type', tracking=True, required=True)
    state = fields.Selection('get_state_value', string='State', copy=True, required=True)
    message = fields.Char('Message')

    def get_operators(self):
        return [
            ('>', '>'), ('<', '<'), ('=', '='), ('>=', '>='), ('<=', '<='), ('<>', '<>')
        ]

    def get_type_alert_value(self):
        return [
            ('limit', 'Limit'), ('alert', 'Alert')
        ]

    def get_state_value(self):
        return [
            ('init', _('Init')), ('conform', _('Conform')), ('not_conform', _('Not Conform')),
            ('unconclusive', _('Inconclusive'))
        ]

    def get_values(self):
        self.ensure_one()
        return {
            'operator_from': self.operator_from,
            'limit_value_from': self.limit_value_from,
            'operator_to': self.operator_to,
            'limit_value_to': self.limit_value_to,
            'type_alert': self.type_alert,
            'state': self.state,
            'message': self.message
        }

