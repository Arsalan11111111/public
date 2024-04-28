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


class LimsParameterPack(models.Model):
    _name = 'lims.parameter.pack'
    _order = 'sequence, name'
    _description = 'Parameter Pack'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    name = fields.Char('Name', required=True, translate=True, index=True, tracking=True)
    sequence = fields.Integer(default=1, index=True)
    product_id = fields.Many2one('product.product', 'Product', index=True, tracking=True,
                                 help='Defines the sales product of this parameter group, if this parameter group is '
                                      'also defined as Billable, then it is added to the list of items when generating '
                                      'the sale order from an analysis request')
    parameter_ids = fields.One2many('lims.parameter.pack.line', 'pack_id', string='Parameter', tracking=True)
    matrix_id = fields.Many2one('lims.matrix', 'Matrix', required=True, index=True, tracking=True,
                                help='Defines the matrix of the parameter group, also adds a filter on the matrix '
                                     'in the list of parameters.')
    labo_id = fields.Many2one('lims.laboratory', string='Labo', required=True, default=get_default_laboratory, tracking=True)
    active = fields.Boolean(tracking=True)
    regulation_id = fields.Many2one('lims.regulation', 'Regulation', required=True, tracking=True,
                                    help='Defines the matrix of the parameter group, also adds a filter on the matrix '
                                         'in the list of parameters.')
    duration = fields.Float('Duration')
    is_pack_of_pack = fields.Boolean('Pack of packs', tracking=True,
                                     help='Pass this group in grouping of parameter group, as soon as this option '
                                          'is active, deletes the list of parameters and its contents during '
                                          'the next recording.')
    parent_id = fields.Many2one('lims.parameter.pack', 'Parent Pack')
    child_ids = fields.One2many('lims.parameter.pack', 'parent_id', 'Children Pack')
    pack_of_pack_ids = fields.One2many('lims.parameter.pack.line.item', 'parent_pack_of_pack_id', 'Packs', tracking=True)
    department_id = fields.Many2one('lims.department', 'Department', tracking=True,
                                    help='Defined as the department, the list of departments is limited by '
                                         'the laboratory of this parameter group.')
    version = fields.Integer(tracking=True, readonly=True,
                             help='The version number is incremented each time this group of parameters is validated.')
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancelled', 'Cancelled')],
                             default='draft', tracking=True, copy=False)
    internal_reference = fields.Char('Internal Reference', tracking=True)
    tag_ids = fields.Many2many('lims.parameter.pack.tag', string='Tags')
    kanban_state = fields.Selection([
        ('normal', 'In progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')
    ], string='Kanban State', default='normal', required=True)

    def get_field_to_test(self):
        # Todo remove obsolete elements.
        return [u'sequence', u'active', u'warning_time', u'version', u'state', u'comment_postfix',
                u'comment_prefix', u'message_follower_ids', u'kanban_state']

    def write(self, vals):
        """
        Checks that the element is not validated to modify fields.
        A list of excluded fields is defined with the 'get_field_to_test' function.
        This function is avoided for demonstration data.
        This allows for the progressive installation of lims modules with demonstration data.
        :param vals:
        :return:
        """
        res_config = self.env['ir.config_parameter'].sudo().get_param('is_parameter_and_pack_protected')
        field_to_test = self.get_field_to_test()
        if res_config and not self.env.context.get('install_mode') and self.filtered(
                lambda r: r.state == 'validated') and bool(set(vals.keys()) - set(field_to_test)):
            raise exceptions.ValidationError(_('You can not change if the pack is "validated"'))
        return super(LimsParameterPack, self).write(vals)

    def unlink(self):
        if self.filtered(lambda p: p.state == 'validated'):
            raise exceptions.ValidationError(_("You can't delete a validated pack."))
        return super().unlink()

    def do_draft(self):
        self.write({
            'state': 'draft',
            'kanban_state': 'normal'
        })

    def do_cancel(self):
        self.write({
            'state': 'cancelled',
            'kanban_state': 'normal'
        })

    def do_validate(self):
        self.write({
            'state': 'validated',
            'kanban_state': 'normal'
        })
        for record in self:
            record.version += 1

    def create_pack_line_item(self):
        line_item_obj = self.env['lims.parameter.pack.line.item']
        for record in self.filtered(lambda r: r.child_ids):
            for child in record.child_ids:
                line_item_obj.create({
                    'parent_pack_of_pack_id': record.id,
                    'pack_id': child.id
                })

    @api.constrains('is_pack_of_pack', 'parent_id')
    def check_pack_of_packs(self):
        for record in self:
            if record.is_pack_of_pack and record.parameter_ids:
                raise exceptions.ValidationError(_('You can not have parameters if the pack is a pack of packs'))
            if not record.is_pack_of_pack and record.child_ids:
                raise exceptions.ValidationError(_('You can not have children packs if the pack is not a pack of packs'))

    @api.constrains('parameter_ids', 'matrix_id')
    def check_matrix_parameter_pack_line(self):
        for record in self:
            wrong_parameter = record.parameter_ids.mapped('method_param_charac_id').filtered(
                lambda p: p.matrix_id != record.matrix_id)
            if wrong_parameter:
                parameter_name = ''
                for parameter in wrong_parameter:
                    parameter_name += parameter.tech_name
                    parameter_name += ' ' if len(wrong_parameter) == 1 else ', '
                raise exceptions.ValidationError(_('{} have not the same matrix').format(parameter_name))

    def duplicate_all(self):
        """
        Copy the parameter pack with parameter
        :return: the view of the new parameter pack if one
        """
        if self.env.context.get('active_ids'):
            parameter_pack_obj = self.env['lims.parameter.pack']
            parameter_pack_ids = parameter_pack_obj.browse(self.env.context.get('active_ids'))
            parameter_pack_line_obj = self.env['lims.parameter.pack.line']
            for parameter_pack in parameter_pack_ids:
                duplicate_parameter_pack = parameter_pack.copy(default={
                                        'name': '{} (copy)'.format(parameter_pack.name),
                                        'active': True,
                                        'version': 0
                                        })
                parameter_pack_obj += duplicate_parameter_pack
                for parameter in parameter_pack.parameter_ids:
                    vals = {'pack_id': parameter.pack_id.id,
                            'method_param_charac_id': parameter.method_param_charac_id.id,
                            'sequence': parameter.sequence,
                            }
                    duplicate_parameter_pack.parameter_ids += parameter_pack_line_obj.create(vals)
            return {'name': _('Parameter Pack'),
                    'view_mode': 'tree,form',
                    'res_model': 'lims.parameter.pack',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'domain': [('id', 'in', parameter_pack_obj.ids)],
                    }
        else:
            raise exceptions.UserError('You should select at least one parameter pack')

    def get_distinct_packs(self, packs_list):
        packs = self.env['lims.parameter.pack']
        for pack in packs_list:
            # Handling pack._origin.id == pack.id
            if pack.ids[0] not in packs.ids:
                packs += pack
        return packs

    def toggle_active(self,*args,**kwargs):
        self.do_draft()

        res = super().toggle_active(*args,**kwargs)
        return res
