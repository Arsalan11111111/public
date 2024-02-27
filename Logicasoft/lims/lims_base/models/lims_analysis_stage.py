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
from odoo import fields, models, _, api, exceptions


class LimsAnalysisStage(models.Model):
    _name = 'lims.analysis.stage'
    _order = 'sequence, id'
    _description = 'Analysis Stage'

    name = fields.Char('Name', required=True, translate=True, index=True)
    type = fields.Selection('get_analysis_stage_type', 'Type', index=True, required=True)
    is_fold = fields.Boolean('Folded')
    sequence = fields.Integer(default=10)

    @api.constrains('type')
    def _check_unicity(self):
        """
        Check if the type is only one in the database
        :return:
        """
        self.ensure_one()
        if self.env['lims.analysis.stage'].search_count([('type', '=', self.type)]) > 1:
            raise exceptions.ValidationError(_('There must be only one analysis stage with the same type.'))

    def get_analysis_stage_type(self):
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
            ('validated1', _('Validated')),
            ('validated2', _('Second Validation')),
            ('cancel', _('Cancelled')),
        ]
