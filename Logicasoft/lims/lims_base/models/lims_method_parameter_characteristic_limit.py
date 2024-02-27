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


class LimsMethodParameterCharacteristic(models.Model):
    _name = 'lims.method.parameter.characteristic.limit'
    _order = 'sequence, id'
    _description = 'Parameter Limit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _tracking_parent = 'method_param_charac_id'

    sequence = fields.Integer(default=1)
    limit_value_from = fields.Float('Limit Value From', digits='Analysis Result', tracking=True)
    limit_value_to = fields.Float('Limit Value To', digits='Analysis Result', tracking=True)
    operator_from = fields.Selection([('>', '>'), ('<', '<'), ('=', '='), ('>=', '>='), ('<=', '<='),
                                      ('<>', '<>')], 'Operator From', tracking=True, default='>=', required=True)
    operator_to = fields.Selection([('>', '>'), ('<', '<'), ('=', '='), ('>=', '>='), ('<=', '<='),
                                    ('<>', '<>')], 'Operator To', tracking=True)
    type_alert = fields.Selection([('limit', 'Limit'), ('alert', 'Alert')], 'Type', tracking=True,
                                  required=True, default='limit')
    state = fields.Selection([('init', _('Init')), ('conform', _('Conform')),
                              ('not_conform', _('Not Conform')), ('unconclusive', _('Inconclusive'))], string='State',
                             required=True, copy=True, default='unconclusive', tracking=True)
    message = fields.Char('Message', translate=True)
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True,
                                             ondelete='cascade')

    def name_get(self):
        result = []
        for record in self:
            display_name = "{} {}".format(record.operator_from, record.limit_value_from)
            if record.operator_to:
                display_name += " {} {}".format(record.operator_to, record.limit_value_to)
            display_name += " {}".format(record.state)
            result.append((record.id, display_name))
        return result
