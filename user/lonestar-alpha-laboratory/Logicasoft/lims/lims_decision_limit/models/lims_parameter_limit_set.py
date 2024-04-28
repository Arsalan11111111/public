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
from odoo import models, fields, api, exceptions, _


class LimsParameterLimitSet(models.Model):
    _name = 'lims.parameter.limit.set'
    _description = 'Parameter Limit Set'

    active = fields.Boolean('Active', default=True)
    parameter_id = fields.Many2one('lims.parameter', domain="['|',('format','=','nu'), ('format','=','ca')]",
                                   required=True)
    report_limit_value = fields.Char('Report Limit Value', translate=True)
    limit_ids = fields.One2many('lims.parameter.limit', 'limit_set_id')
    limit_count = fields.Integer(compute='_get_limit_count')

    matrix_id = fields.Many2one('lims.matrix')
    regulation_id = fields.Many2one('lims.regulation')
    partner_id = fields.Many2one('res.partner')
    product_id = fields.Many2one('product.product', domain="[('lims_for_analysis','=',True)]",
                                 context="{'default_lims_for_analysis':True}")

    def name_get(self):
        result = []
        for record in self:
            display_name = f"{record.parameter_id.name}{f':{record.report_limit_value}' if record.report_limit_value else ''}"
            result.append((record.id, display_name))
        return result

    def open_limit_ids(self):
        """
        Open view on limits for editing it
        :return:
        """
        return {'name': _('Parameter limit set'),
                'view_mode': 'form',
                'res_model': 'lims.parameter.limit.set',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.id,
                }

    @api.depends('limit_ids')
    def _get_limit_count(self):
        for record in self:
            record.limit_count = len(record.limit_ids)
