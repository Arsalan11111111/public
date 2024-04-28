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


class LimsResultValue(models.Model):
    _name = 'lims.result.value'
    _description = 'Result Value'
    _order = 'sequence asc, name asc'

    def get_default_parameter_ids(self):
        if 'rel_parameter_id' in self.env.context:
            return [(6, 0, [self.env.context['rel_parameter_id']])]
        return False

    def compute_color(self):
        for record in self:
            if record.state == 'init':
                record.color = 8
            elif record.state == 'conform':
                record.color = 10
            elif record.state == 'not_conform':
                record.color = 1
            else:
                record.color = 0

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer(default=1)
    parameter_ids = fields.Many2many('lims.parameter', 'rel_parameter_value', 'value_id', 'parameter_id', 'Parameter',
                                     default=get_default_parameter_ids)
    state = fields.Selection([('init', _('Init')), ('conform', _('Conform')), ('not_conform', _('Not Conform')),
                              ('unconclusive', _('Inconclusive'))], string='State', default='unconclusive')
    description = fields.Char()
    active = fields.Boolean(default=True)
    color = fields.Integer(compute=compute_color)
    message = fields.Char('Message', translate=True, help='This message is automatically filled in the comment of '
                                                          'the result when this value is selected.')

    def open_result(self):
        """
        Open view for results (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Sel result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.sel.result',
            'view_mode': 'tree,calendar',
            'domain': [('value_id', '=', self.id)],
            'context': {'active_test': False},
        }
