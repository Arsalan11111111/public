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
from odoo import models, fields, api, _


class LimsParameterCharPartner(models.Model):
    _name = 'lims.parameter.char.partner'
    _description = 'Parameter Char Partner'
    _rec_name = 'partner_id'

    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True,
                                             ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    reference = fields.Char('Reference',
                            help="This field is used for the IDE,"
                                 "\n it links a lims parameter according to the name given in the partner file.")
    comment = fields.Char('Comment')
    factor = fields.Float('Factor', default=1.0,
                          help="The factor is used when importing results of EDI via this partner. "
                               "\nIt is applied as follows result of the partner x factor = result in the lims")
    matrix_id = fields.Many2one('lims.matrix', string='Matrix')
    limit_ids = fields.One2many('lims.method.parameter.characteristic.limit.partner', 'parameter_char_partner_id')
    report_limit_value = fields.Char('Report Limit Value', translate=True)
    rel_regulation_id = fields.Many2one('lims.regulation', related='method_param_charac_id.regulation_id')

    def open_limit(self):
        """
        Open view on limits for editing it
        :return:
        """
        return {'name': _('Parameter Char Partner'),
                'view_mode': 'form',
                'res_model': 'lims.parameter.char.partner',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.id,
                }
