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
from odoo.exceptions import UserError


class LimsMethodParameterCharacteristic(models.Model):
    _name = 'lims.method.parameter.characteristic'
    _description = 'Method Parameter Characteristic'
    _rec_name = 'tech_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        return self.env.user.default_laboratory_id or self.env['lims.laboratory'].search(
            [('default_laboratory', '=', True)])

    method_id = fields.Many2one('lims.method', 'Method', required=True, tracking=True)
    matrix_type_id = fields.Many2one(related='matrix_id.type_id', store=True, readonly=True, string='Matrix Type')
    matrix_id = fields.Many2one('lims.matrix', 'Matrix', required=True, tracking=True)
    parameter_id = fields.Many2one('lims.parameter', 'Parameter', required=True, tracking=True)
    loq = fields.Float('LOQ', digits='Analysis Result', tracking=True)
    lod = fields.Float('LOD', digits='Analysis Result', tracking=True)
    ls = fields.Float('LS', digits='Analysis Result', tracking=True)
    recovery = fields.Float('Recovery', digits='Analysis Result', tracking=True)
    u = fields.Float('U', digits='Analysis Result', tracking=True)
    u_char = fields.Char('U(char)', tracking=True)
    auto_valid = fields.Boolean('Automatic validation', tracking=True,
                                help='If active, allows the generated result of this parameter characteristic to go '
                                     'from the stage \"done\" directly to the stage (first) \"Validated\".')
    tech_name = fields.Char('Technical Name', tracking=True, translate=True, copy=False,
                            help='This text is the label that will be used for the encoding form views.')
    accreditation = fields.Selection([('inta', 'Internal Accredited'), ('intna', ' Internal Not Accredited'),
                                      ('exta', 'External Accredited'), ('extna', 'External Not Accredited')],
                                     string='Accreditation Type', tracking=True, default='intna')
    uom = fields.Many2one('uom.uom', tracking=True)
    regulation_id = fields.Many2one('lims.regulation', 'Regulation', required=True, tracking=True)
    name = fields.Char('Name', compute='get_name', readonly=True, store=True, tracking=True)
    laboratory_id = fields.Many2one('lims.laboratory', string='Laboratory', required=True, tracking=True,
                                    default=get_default_laboratory)
    parameter_pack_count = fields.Integer(compute='get_parameter_pack_count', tracking=True)
    format = fields.Selection(related='parameter_id.format', readonly=True, tracking=True, store=True)
    active = fields.Boolean(tracking=True)
    limit_ids = fields.One2many('lims.method.parameter.characteristic.limit', 'method_param_charac_id', tracking=True)
    nbr_dec_showed = fields.Integer('Number of decimal in the report', default=2, tracking=True)

    # fields for computed parameters
    formula = fields.Char(tracking=True)
    correspondence_ids = fields.One2many('lims.parameter.compute.correspondence', 'compute_parameter_id',
                                         'Table of correspondences', tracking=True)
    use_function = fields.Boolean('Use function', help='Formula will use complex math function and not just simple '
                                                       'operators')
    use_loq = fields.Boolean('Formula LOQ',
                             help='If the value of the results used in the formula is smaller than result loq, the '
                                  'value interpreted on the formula will be 0')

    char1 = fields.Char(tracking=True)
    char2 = fields.Char(tracking=True)
    work_instruction_id = fields.Many2one('lims.work.instruction', string='Work Instruction', tracking=True)
    mloq = fields.Float('mLOQ', digits='Analysis Result', tracking=True)
    accreditation_ids = fields.Many2many('lims.accreditation', string='Organisms')
    department_id = fields.Many2one(related='method_id.department_id', store=True, readonly=True, tracking=True)
    not_check_loq = fields.Boolean('Not check LOQ in report')
    not_check_max_value = fields.Boolean('Not check Max Value in report', default=True)
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancelled', 'Cancelled')],
                             default='draft', tracking=True, copy=False)
    analytical_technique_id = fields.Many2one('lims.analytical.technique', string='Analytical Technique', tracking=True)
    standard_ids = fields.Many2many('lims.standard', string='Standard', tracking=True)
    ref = fields.Char('', tracking=True)
    ulow = fields.Float('Ulow', digits='Analysis Result', tracking=True)
    uaverage = fields.Float('Uaverage', digits='Analysis Result', tracking=True)
    uhigh = fields.Float('Uhigh', digits='Analysis Result', tracking=True)
    kanban_state = fields.Selection([
        ('normal', 'In progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')
    ], string='Kanban State', default='normal', required=True)

    conditional_parameters_ids = fields.Many2many('lims.method.parameter.characteristic',
                                                  'lims_method_parameter_characteristic_rel', 'parameter_charac_id',
                                                  'conditional_parameter_charac_id',
                                                  string="Conditional Parameters")
    significant_figure = fields.Integer("Significant figure", default=4)
    decimal_loq_showed = fields.Integer('Number of decimal of LOQ in the report', default=3, tracking=True)
    format_number_report = fields.Selection(selection="get_selection_format_number_report",
                                            string="Format number in report", default='decimal')
    product_id = fields.Many2one('product.product', 'Product', tracking=True)
    nb_history = fields.Integer(default=10, string='NB History')

    def get_selection_format_number_report(self):
        return [
            ('significant_figure', _('Significant Figure')),
            ('decimal', _('Decimal')),
            ('both', _('Significant with decimal limit')),
            ('scientific', _('Scientific')),
            ('engineering', _('Engineering')),
            ('none', _('Nothing'))
            ]

    @api.onchange('significant_figure', 'decimal_loq_showed', 'nbr_dec_showed')
    def on_change_significant(self):
        for record in self:
            if record.significant_figure < 0:
                raise UserError(_('Significant number must be superior to 0'))
            if record.decimal_loq_showed < 0:
                raise UserError(_('Decimal number loq must be superior to 0'))
            if record.nbr_dec_showed < 0:
                raise UserError(_('Decimal number must be superior to 0'))

    def unlink(self):
        if self.filtered(lambda p: p.state == 'validated'):
            raise exceptions.ValidationError(_("You can't delete a validated parameter"))
        return super().unlink()

    def do_draft(self):
        self.write({
            'state': 'draft',
            'kanban_state': 'normal'
        })

    def do_cancel(self):
        self.write({
            'state': 'cancelled',
            'kanban_state': 'normal',
        })

    def do_validate(self):
        self.write({
            'state': 'validated',
            'kanban_state': 'normal',
        })

    @api.constrains('matrix_id')
    def check_parameter_pack_matrix(self):
        for record in self:
            line_ids = self.env['lims.parameter.pack.line'].search([('method_param_charac_id', '=', record.id)])
            if line_ids and line_ids.mapped('pack_id').filtered(lambda pack: pack.matrix_id != record.matrix_id):
                raise exceptions.ValidationError(_('Pack and parameters must have the same matrix'))

    def get_field_to_test(self):
        # Todo remove obsolete elements
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
        if vals.get('parameter_id'):
            results_exist = self.check_result_exist()
            if vals.get('parameter_id') != self.parameter_id.id and results_exist:
                raise exceptions.ValidationError(
                    _("You can't change the parameter of a characteristic with results : {}").format(
                        vals.get('name') or self.name))
        res_config = self.env['ir.config_parameter'].sudo().get_param('is_parameter_and_pack_protected')
        field_to_test = self.get_field_to_test()
        if res_config and not self.env.context.get('install_mode') and self.filtered(
                lambda r: r.state == 'validated') and (set(vals.keys()) - set(field_to_test)):
            raise exceptions.ValidationError(_('You can not change if the parameter is "validated"'))
        if 'use_function' in vals and not vals.get('use_function'):
            self.mapped('correspondence_ids').write({'is_optional': False})
        return super(LimsMethodParameterCharacteristic, self).write(vals)

    def check_result_exist(self):
        result_id = self.env['lims.analysis.numeric.result'].with_context(active_test=False).search(
            [('method_param_charac_id', 'in', self.filtered(lambda p: p.format == 'nu').ids)], count=True, limit=1)
        result_id = result_id or self.env['lims.analysis.compute.result'].with_context(active_test=False).search(
                [('method_param_charac_id', 'in', self.filtered(lambda p: p.format == 'ca').ids)], count=True, limit=1)
        result_id = result_id or self.env['lims.analysis.sel.result'].with_context(active_test=False).search(
                [('method_param_charac_id', 'in', self.filtered(lambda p: p.format == 'se').ids)], count=True, limit=1)
        result_id = result_id or self.env['lims.analysis.text.result'].with_context(active_test=False).search(
                [('method_param_charac_id', 'in', self.filtered(lambda p: p.format == 'tx').ids)], count=True, limit=1)
        return result_id

    def open_wizard_create_parameter_pack(self):
        """
        Open the wizard for create parameter pack
        :return:
        """
        return {
            'name': 'Create Parameter Pack',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'create.parameter.pack.wizard',
            'context': {'default_method_parameter_characteristic_ids': self.ids},
            'target': 'new',
        }

    @api.depends('regulation_id', 'regulation_id.name', 'matrix_id', 'matrix_id.name', 'parameter_id',
                 'parameter_id.name')
    def get_name(self):
        """
        Compute the name depends on regulation, matrix, parameter
        :return:
        """
        for record in self:
            record.name = '[%s] - [%s] - [%s]' % \
                          (record.regulation_id.name, record.matrix_id.name, record.parameter_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        """
        IF the user dont give the tech_name, compute it, create the record
        :param vals:
        :return:
        """
        for vals in vals_list:
            parameter_id = self.env['lims.parameter'].browse(vals.get('parameter_id'))
            if not vals.get('tech_name') and vals.get('parameter_id'):
                vals['tech_name'] = parameter_id.name
            vals['ref'] = parameter_id.ref
        return super(LimsMethodParameterCharacteristic, self).create(vals_list)

    def get_parameter_pack_count(self):
        """
        Compute the number of parameter pack where is the method parameter characteristic
        :return:
        """
        if self.ids:
            counted_data = self.env['lims.parameter.pack.line'].read_group([('method_param_charac_id', 'in', self.ids)], ['method_param_charac_id'], ['method_param_charac_id'])
            mapped_data = { count['method_param_charac_id'][0]: count['method_param_charac_id_count'] for count in counted_data }
        else:
            mapped_data = {}

        for record in self:
            record.parameter_pack_count = mapped_data.get(record.id, 0)

    @api.constrains('parameter_id', 'regulation_id', 'matrix_id', 'method_id', 'laboratory_id', 'active')
    def _check_unicity(self):
        """
        Check if only one record exists with the same parameter, regulation, matrix, method, laboratory
        :return:
        """
        for record in self:
            if self.env['lims.method.parameter.characteristic'].search_count([
                ('parameter_id', '=', record.parameter_id.id),
                ('regulation_id', '=', record.regulation_id.id),
                ('matrix_id', '=', record.matrix_id.id),
                ('laboratory_id', '=', record.laboratory_id.id),
                ('method_id', '=', record.method_id.id),  '|',
                ('active', '=', True),
                ('active', '=', False)]
            ) > 1:
                raise exceptions.ValidationError(_('There must be only one parameter characteristic with the same '
                                                   'parameter, regulation, matrix, laboratory and method.'))

    def open_parameter_pack(self):
        """
        Open the parameter pack where the method parameter characteristic is in
        :return:
        """
        self.ensure_one()
        return {
            'name': _('Parameter Pack'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.parameter.pack',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('parameter_ids.method_param_charac_id', '=', self.id)],
        }

    def get_values_for_copy(self):
        """
        return values for method duplicate_all.
        :return: dict with all default values
        """
        return {
            'default_matrix_id': self.matrix_id.id,
            'default_parameter_id': self.parameter_id.id,
            'default_loq': self.loq,
            'default_lod': self.lod,
            'default_ls': self.ls,
            'default_recovery': self.recovery,
            'default_u': self.u,
            'default_auto_valid': self.auto_valid,
            'default_accreditation': self.accreditation,
            'default_uom': self.uom.id,
            'default_regulation_id': self.regulation_id.id,
            'default_laboratory_id': self.laboratory_id.id,
            'default_nbr_dec_showed': self.nbr_dec_showed,
            'default_formula': self.formula,
            'default_use_function': self.use_function,
            'default_char1': self.char1,
            'default_char2': self.char2,
            'default_work_instruction_id': self.work_instruction_id.id,
            'default_mloq': self.mloq,
            'default_accreditation_ids': self.accreditation_ids.ids
        }

    def duplicate_all(self):
        """
        Should copy without the method_id. But copy() can't be used because method_id is a required field :
        We can't copy with the method because of unicity rules, and we can't copy without the method because field is
        required
        :return: action to create a new parameter char with pre-filled fields
        """
        self.ensure_one()
        context = self.get_values_for_copy()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lims.method.parameter.characteristic',
            'view_mode': 'form',
            'context': context,
        }

    def duplicate_all_regulation(self):
        self.ensure_one()
        context = self.get_values_for_copy()
        context.update({
            'default_method_id': self.method_id.id,
            'default_regulation_id': False,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lims.method.parameter.characteristic',
            'view_mode': 'form',
            'context': context,
        }

    def compute_formula_wizard(self):
        context=self.env.context.copy()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'parameter.compute.correspondence.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def get_result_table(self):
        """
        Get the table of the result create from this parameter (according to format)
        """
        self.ensure_one()
        format = self.format
        if format == 'nu':
            return 'lims.analysis.numeric.result'
        if format == 'se':
            return 'lims.analysis.sel.result'
        elif format == 'ca':
            return 'lims.analysis.compute.result'
        elif format == 'tx':
            return 'lims.analysis.text.result'

    def toggle_active(self):
        self.do_draft()
        res = super().toggle_active()
        return res
