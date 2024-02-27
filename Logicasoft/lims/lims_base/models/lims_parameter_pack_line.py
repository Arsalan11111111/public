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
from odoo import fields, models, api


class LimsParameterPackLine(models.Model):
    _name = 'lims.parameter.pack.line'
    _order = 'sequence, id'
    _description = 'Parameter Pack Line'
    _inherit = ['mail.thread']
    _tracking_parent = 'pack_id'

    sequence = fields.Integer(default=1)
    pack_id = fields.Many2one('lims.parameter.pack', 'Parameter Pack', ondelete='cascade')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True,
                                             ondelete='cascade')
    method_id = fields.Many2one(related='method_param_charac_id.method_id', readonly=1)
    matrix_id = fields.Many2one(related='method_param_charac_id.matrix_id', readonly=1)
    name = fields.Char(related='method_param_charac_id.tech_name', readonly=1)
    active = fields.Boolean(default=True, tracking=True)
    rel_department_id = fields.Many2one(related='method_param_charac_id.department_id', readonly=1)
    rel_regulation_id = fields.Many2one(related='method_param_charac_id.regulation_id')
    rel_state = fields.Selection(related='method_param_charac_id.state', string="State of parameter", readonly=1)

    @api.onchange('method_param_charac_id')
    def onchange_method_param_charac_id(self):
        if self.pack_id:
            domain = [('matrix_id', '=', self.pack_id.matrix_id.id),
                      ('regulation_id', '=', self.pack_id.regulation_id.id), ('state', '=', 'validated')]
            if self.pack_id.department_id:
                domain.append(('department_id', '=', self.pack_id.department_id.id))
            return {
                'domain': {'method_param_charac_id': domain}
            }
