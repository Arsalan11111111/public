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


class LimsMethod(models.Model):
    _name = 'lims.method'
    _description = 'Method'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def get_default_stages(self):
        return self.env['lims.method.stage'].search([('is_default', '=', True)])

    name = fields.Char('Name', required=True, translate=True, index=True)
    active = fields.Boolean(tracking=True, default=True)
    standard_ids = fields.Many2many('lims.standard', string='Standard')
    product_id = fields.Many2one('product.product', 'Product', index=True)
    time = fields.Float('Time')
    time_technician = fields.Float('Technician time')
    method_param_charac_ids = fields.One2many('lims.method.parameter.characteristic', 'method_id')
    department_id = fields.Many2one('lims.department', 'Department', index=True, required=True)
    label_name = fields.Char('Label Name', index=True, translate=True, default='/')
    comment = fields.Html('Comment', translate=True)
    rel_labo_id = fields.Many2one(related="department_id.labo_id", store=True, readonly=True,
                                  help="This is the 'Laboratory' of the department of that method.")
    is_auto_cancel = fields.Boolean('Auto Cancel',
                                    help="This option allows to close the tests which have a 'to do' status for a long "
                                         "time. Depending on the configured duration.")
    auto_cancel_time = fields.Float('Time Cancel',
                                    help="This duration indicates the maximum duration of a test in 'todo' status "
                                         "before the lims automatically cancel it; if this value is negative or zero "
                                         "then it will not be taken.")
    container_ids = fields.One2many('lims.method.container', 'method_id', string='Containers')
    nb_label_total = fields.Integer('Number of label')
    separator = fields.Char('Separator')
    attribute_ids = fields.One2many('lims.method.attribute', 'method_id', string='Attribute')
    work_instruction_id = fields.Many2one('lims.work.instruction', string='Work Instruction')
    analytical_technique_id = fields.Many2one('lims.analytical.technique', string='Analytical Technique')
    method_ids = fields.Many2many('lims.method', 'lims_method_rel', 'parent_id', 'child_id')
    preservative = fields.Char('Preservative')
    sequence = fields.Integer(string="Sequence")
    stage_ids = fields.Many2many('lims.method.stage', 'method_method_stage_rel', 'method_id', 'stage_id', 'Stages',
                                 default=get_default_stages)
    rel_labo_users_ids = fields.Many2many('res.users', related="rel_labo_id.res_users_ids", string="Lab User",
                                          help="This is the 'Users' of the laboratory of that method.")

    @api.onchange('container_ids', 'department_id')
    def get_nb_label(self):
        """
        Set number of label total (used for print)
        :return:
        """
        if not self.env['ir.config_parameter'].sudo().get_param('deactivate.container.label'):
            if not self.container_ids and self.department_id:
                self.nb_label_total = self.department_id.labo_id and self.department_id.labo_id.nb_print_sop_label
            else:
                self.nb_label_total = sum([container.qty for container in self.container_ids])

    @api.model_create_multi
    def create(self, vals_list):
        """
        Extend create function to automate methods' stages creation
        :param vals_list: Dictionary of values to create
        :return: Created object
        """
        for vals in vals_list:
            if vals.get('label_name') and vals.get('label_name') == '/':
                vals['label_name'] = vals.get('name')
        method = super().create(vals_list)
        return method
