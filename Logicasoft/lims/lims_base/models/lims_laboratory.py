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
from odoo import fields, models, api, exceptions, _
from random import randint


class LimsLaboratory(models.Model):
    _name = 'lims.laboratory'
    _description = 'Laboratory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, translate=True, index=True)
    responsible_id = fields.Many2one('hr.employee.public', 'Responsible', index=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner', index=True, tracking=True)
    seq_analysis_id = fields.Many2one('ir.sequence', 'Sequence Analysis', index=True, tracking=True,
                                      help="Sequence used to set the name of the analysis.")
    seq_sop_id = fields.Many2one('ir.sequence', 'Sequence test', index=True, tracking=True,
                                 help="Sequence used to set the name of the test.")
    seq_request_id = fields.Many2one('ir.sequence', 'Sequence Request', index=True, tracking=True,
                                     help="Sequence used to set the name of the request.")
    seq_batch_id = fields.Many2one('ir.sequence', 'Sequence Batch', index=True, tracking=True,
                                   help="Sequence used to set the name of the batch.")
    nb_print_sop_label = fields.Integer('Number test Label', help='Default number of prints by test for labels',
                                        default=1, tracking=True)
    default_laboratory = fields.Boolean('Default Laboratory', tracking=True)
    default_analysis_category_id = fields.Many2one('lims.analysis.category', 'Default Category Analysis', tracking=True)
    default_request_category_id = fields.Many2one('lims.request.category', 'Default Category Request', tracking=True)
    dilution_factor_max = fields.Float('Dilution Factor Max', default=4, tracking=True)
    unconclusive_priority = fields.Boolean('Unconclusvive priority',
                                           help='The inconclusive state has the priority over conform state',
                                           tracking=True)
    only_second_validation = fields.Boolean('Only Validation 2', tracking=True)
    show_result_comment = fields.Boolean('Show result comments', help='Show results comment by default on report',
                                         tracking=True)
    change_loq = fields.Boolean('Change LOQ', help='If checked, LOQ will be editable on results', tracking=True)
    manage_accreditation = fields.Boolean('Manage accreditation on result', tracking=True)
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working time')
    res_users_ids = fields.Many2many(comodel_name='res.users', relation='lims_laboratory_res_users_rel',
                                    column1="lims_laboratory_id",
                                    column2="res_users_id", string="Users", tracking=True,
                                     help="This is the 'Users' of that laboratory.")
    color = fields.Integer('color', default=_get_default_color)

    @api.constrains('default_laboratory')
    def _check_unicity(self):
        """
        Check if there is only one default laboratory in the database
        :return:
        """
        self.ensure_one()
        if self.env['lims.laboratory'].search_count([('default_laboratory', '=', True)]) > 1:
            raise exceptions.ValidationError(_('There must be only one default laboratory.'))
