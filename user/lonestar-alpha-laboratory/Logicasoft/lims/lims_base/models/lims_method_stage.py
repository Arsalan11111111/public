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
from odoo import models, fields, _


class LimsMethodStage(models.Model):
    _name = 'lims.method.stage'
    _order = 'sequence, id'
    _description = 'Method Stage'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    type = fields.Selection('get_type_selection', 'Type')
    method_ids = fields.Many2many('lims.method', 'method_method_stage_rel', 'stage_id', 'method_id', string='Methods')
    sequence = fields.Integer(default=10)
    is_default = fields.Boolean('Stage by default', help='If checked, every new method created will automatically be '
                                                         'linked to this stage')
    is_fold = fields.Boolean('Folded')

    def get_type_selection(self):
        """
        Return different type possible for the stage
        :return: list of tuple
        """
        return [
            ('draft', _('Draft')),
            ('plan', _('Plan')),
            ('todo', _('ToDo')),
            ('wip', _('WIP')),
            ('done', _('Done')),
            ('validated', _('Validated')),
            ('cancel', _('Cancelled'))
        ]

