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


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def laboratory(self):
        return [int(self.env['ir.config_parameter'].sudo().get_param('default_laboratory_ids'))]

    default_laboratory_id = fields.Many2one('lims.laboratory', help='Sets the default lab for this user.')
    laboratory_ids = fields.Many2many(comodel_name='lims.laboratory', relation='lims_laboratory_res_users_rel',
                                      column1="res_users_id",
                                      column2="lims_laboratory_id", default=laboratory, string='Laboratories',
                                      help='List of laboratories assigned for the user.')
    department_ids = fields.Many2many(comodel_name='lims.department', relation='lims_department_res_users_rel',
                                      column1="res_users_id", column2="lims_department_id", string='Departments',
                                      help="This is the departments in which this user is linked.")

    def update_vals_with_department(self, vals):
        department_obj = self.env['lims.department']
        department_ids = []
        laboratory_ids = vals.get('laboratory_ids')[0][2]
        for laboratory_id in laboratory_ids:
            departments = department_obj.search([('labo_id', '=', laboratory_id)])
            department_ids += departments.ids
        vals.update({
            'department_ids': [[6, False, department_ids]]
        })
