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
from odoo import fields, models, api, exceptions


class LimsParameterPackLine(models.Model):
    _name = 'lims.parameter.pack.line.item'
    _description = 'Parameter Pack Line Item'
    _order = 'sequence, id'
    _rec_name = 'pack_id'

    sequence = fields.Integer()
    parent_pack_of_pack_id = fields.Many2one('lims.parameter.pack', 'Parameter Pack', required=True, ondelete='cascade')
    pack_id = fields.Many2one('lims.parameter.pack', 'Pack', required=True, ondelete='cascade')

    rel_matrix_id = fields.Many2one(related='pack_id.matrix_id', readonly=True)
    rel_regulation_id = fields.Many2one(related='pack_id.regulation_id', readonly=True)
    rel_labo_id = fields.Many2one(related='pack_id.labo_id', readonly=True)
    rel_department_id = fields.Many2one(related='pack_id.department_id', readonly=True)
    rel_active = fields.Boolean(related='pack_id.active', readonly=True)
    rel_state = fields.Selection(related='pack_id.state', string="State of pack", readonly=True)

    @api.onchange('pack_id')
    def onchange_method_pack_id(self):
        if not self.parent_pack_of_pack_id.matrix_id or not self.parent_pack_of_pack_id.regulation_id:
            raise exceptions.UserError('You should select matrix_id and regulation_id of the parent pack')

        domain = [
            ('is_pack_of_pack', '=', False),
            ('labo_id', '=', self.parent_pack_of_pack_id.labo_id.id),
            ('state', '=', 'validated'),
            ('matrix_id', '=', self.parent_pack_of_pack_id.matrix_id.id),
            ('regulation_id', '=', self.parent_pack_of_pack_id.regulation_id.id)
        ]
        return {
            'domain': {'pack_id': domain}
        }
