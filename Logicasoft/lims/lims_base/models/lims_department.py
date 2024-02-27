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
from odoo import fields, models


class LimsDepartment(models.Model):
    _name = 'lims.department'
    _description = 'Department'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    name = fields.Char('Name', required=True, translate=True, index=True)
    responsible_id = fields.Many2one('hr.employee.public', 'Responsible', index=True)
    labo_id = fields.Many2one('lims.laboratory', 'Laboratory', index=True, default=get_default_laboratory)
    location = fields.Char(string='Location')
    sequence = fields.Integer(string="Sequence")
    active = fields.Boolean(default=True)
    res_users_ids = fields.Many2many(comodel_name='res.users', relation='lims_department_res_users_rel',
                                    column1="lims_department_id", column2="res_users_id", string="Users", tracking=True)
    rel_labo_users_ids = fields.Many2many('res.users', relation='lims_department_res_users_labo_rel',
                                          column1="lims_department_labo_id", column2="res_users_id",
                                          related='labo_id.res_users_ids', store=True, string='Labo users',
                                          ondelete='cascade',
                                          help="This is the 'Users' of the laboratory of that department.")
    rel_color = fields.Integer(related='labo_id.color', help="This is the 'Color' of the laboratory of that department.")
