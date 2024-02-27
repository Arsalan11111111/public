
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


class AddParametersWizard(models.TransientModel):
    _name = 'add.parameters.wizard'
    _description = 'Add parameters'

    def get_line_ids(self, default_analysis_id=None):
        line_obj = self.env['add.parameters.wizard.line']
        line_ids = line_obj
        default_analysis_id = default_analysis_id or self.env.context.get('default_analysis_id')
        analysis_id = self.env['lims.analysis'].browse(default_analysis_id)
        for result_id in analysis_id.result_num_ids.filtered(lambda r: r.rel_type != 'cancel'):
            vals = {
                'method_param_charac_id': result_id.method_param_charac_id.id,
                'pack_id': result_id.pack_id.id,
                'in_analysis': True,
            }
            line_ids += line_obj.new(vals)

            for method_param_charac_id in result_id.method_param_charac_id.conditional_parameters_ids:
                if method_param_charac_id not in line_ids.mapped('method_param_charac_id'):
                    vals = {
                        'method_param_charac_id': method_param_charac_id.id,
                        'pack_id': result_id.pack_id.id,
                        'in_analysis': True,
                        'is_conditional_parameter': True
                    }
                    line_ids += line_obj.new(vals)

        for result_id in analysis_id.result_sel_ids.filtered(lambda r: r.rel_type != 'cancel'):
            vals = {
                'method_param_charac_id': result_id.method_param_charac_id.id,
                'pack_id': result_id.pack_id.id,
                'in_analysis': True,
            }
            line_ids += line_obj.new(vals)

            for method_param_charac_id in result_id.method_param_charac_id.conditional_parameters_ids:
                if method_param_charac_id not in line_ids.mapped('method_param_charac_id'):
                    vals = {
                        'method_param_charac_id': method_param_charac_id.id,
                        'pack_id': result_id.pack_id.id,
                        'in_analysis': True,
                        'is_conditional_parameter': True
                    }
                    line_ids += line_obj.new(vals)

        for compute_result_id in analysis_id.result_compute_ids.filtered(lambda r:
                                                                         r.rel_type != 'cancel'):
            vals = {
                'method_param_charac_id': compute_result_id.method_param_charac_id.id,
                'pack_id': compute_result_id.pack_id.id,
                'in_analysis': True,
            }
            line_ids += line_obj.new(vals)

            for method_param_charac_id in compute_result_id.method_param_charac_id.conditional_parameters_ids:
                if method_param_charac_id not in line_ids.mapped('method_param_charac_id'):
                    vals = {
                        'method_param_charac_id': method_param_charac_id.id,
                        'pack_id': compute_result_id.pack_id.id,
                        'in_analysis': True,
                        'is_conditional_parameter': True
                    }
                    line_ids += line_obj.new(vals)
        for result_id in analysis_id.result_text_ids.filtered(lambda r: r.rel_type != 'cancel'):
            vals = {
                'method_param_charac_id': result_id.method_param_charac_id.id,
                'pack_id': result_id.pack_id.id,
                'in_analysis': True,
            }
            line_ids += line_obj.new(vals)

            for method_param_charac_id in result_id.method_param_charac_id.conditional_parameters_ids:
                if method_param_charac_id not in line_ids.mapped('method_param_charac_id'):
                    vals = {
                        'method_param_charac_id': method_param_charac_id.id,
                        'pack_id': result_id.pack_id.id,
                        'in_analysis': True,
                        'is_conditional_parameter': True
                    }
                    line_ids += line_obj.new(vals)

        return line_ids.filtered('is_conditional_parameter') + \
               line_ids.filtered(lambda line: not line.is_conditional_parameter)

    line_ids = fields.One2many('add.parameters.wizard.line', 'add_parameters_wizard_id', default=get_line_ids)
    analysis_id = fields.Many2one('lims.analysis')
    rel_matrix_id = fields.Many2one('lims.matrix', related='analysis_id.matrix_id')
    rel_laboratory_id = fields.Many2one('lims.laboratory', related='analysis_id.laboratory_id')
    rel_regulation_id = fields.Many2one('lims.regulation', related='analysis_id.regulation_id')
    parameter_pack_id = fields.Many2one('lims.parameter.pack', string='Parameter Packs')
    method_param_charac_ids = fields.Many2many('lims.method.parameter.characteristic', string='Parameters')

    @api.onchange('rel_regulation_id')
    def onchange_regulation(self):
        if self.rel_regulation_id:
            return {'domain': {'parameter_pack_id': [('regulation_id', '=', self.rel_regulation_id.id),
                                                     ('matrix_id', '=', self.rel_matrix_id.id),
                                                     ('labo_id', '=', self.rel_laboratory_id.id)],
                               'method_param_charac_ids': [('regulation_id', '=', self.rel_regulation_id.id),
                                                           ('matrix_id', '=', self.rel_matrix_id.id),
                                                           ('laboratory_id', '=', self.rel_laboratory_id.id),
                                                           ('state', '=', 'validated')]
                               }
                    }
        else:
            return {'domain': {'parameter_pack_id': [('matrix_id', '=', self.rel_matrix_id.id),
                                                     ('labo_id', '=', self.rel_laboratory_id.id)],
                               'method_param_charac_ids': [('matrix_id', '=', self.rel_matrix_id.id),
                                                           ('laboratory_id', '=', self.rel_laboratory_id.id),
                                                           ('state', '=', 'validated')]
                               }
                    }

    @api.onchange('parameter_pack_id')
    def onchange_parameter_pack_id(self):
        """
        When a parameter pack is added create results for its parameters.
        :return: (None)
        """
        self.create_line_from_pack(self.parameter_pack_id)

    def create_line_from_pack(self, pack_id):
        line_obj = self.env['add.parameters.wizard.line']
        all_pack = self.env['lims.parameter.pack']
        all_pack += pack_id.filtered(lambda p: not p.is_pack_of_pack)
        all_pack += pack_id.filtered(lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids').filtered(
            lambda x: x.rel_active and x.rel_state == 'validated').pack_id
        for parameter_pack_line in all_pack.mapped('parameter_ids').filtered(lambda x: x.active and x.rel_state == 'validated'):
            method_param_charac_id = parameter_pack_line.method_param_charac_id
            if method_param_charac_id not in self.line_ids.mapped('method_param_charac_id'):
                vals = {
                    'method_param_charac_id': method_param_charac_id.id,
                    'pack_id': parameter_pack_line.pack_id.id,
                }
                self.line_ids += line_obj.new(vals)

                for conditional_method_param_charac_id in method_param_charac_id.conditional_parameters_ids:
                    if conditional_method_param_charac_id not in self.line_ids.mapped('method_param_charac_id'):
                        vals = {
                            'method_param_charac_id': conditional_method_param_charac_id.id,
                            'pack_id': parameter_pack_line.pack_id.id,
                            'is_conditional_parameter': True
                        }
                        self.line_ids += line_obj.new(vals)

            if not self.rel_regulation_id:
                self.analysis_id.regulation_id = method_param_charac_id.regulation_id

        self.line_ids = self.line_ids.filtered('is_conditional_parameter') + \
                        self.line_ids.filtered(lambda line: not line.is_conditional_parameter)

    @api.onchange('method_param_charac_ids')
    def onchange_parameter_characteristic_id(self):
        """
        When a parameter is added create result for it.
        :return: (None)
        """
        line_obj = self.env['add.parameters.wizard.line']
        line_to_delete = self.line_ids.filtered(lambda line: line.from_parameter_characteristic_ids)
        if line_to_delete:
            # I change line_to_save for line_to_delete because it doesn't remove line_id in line_ids
            # when i remove param in method_param_charac_ids
            self.update({'line_ids': [(2, line.id) for line in line_to_delete]})
        if self.method_param_charac_ids:
            for method_param_charac_id in self.method_param_charac_ids:
                if method_param_charac_id._origin.id not in self.line_ids.mapped('method_param_charac_id').ids:
                    vals = {
                        'method_param_charac_id': method_param_charac_id._origin.id,
                        'from_parameter_characteristic_ids': True,
                    }
                    self.line_ids += line_obj.new(vals)

                    for conditional_method_param_charac_id in method_param_charac_id.conditional_parameters_ids:
                        if conditional_method_param_charac_id._origin.id not in \
                                self.line_ids.mapped('method_param_charac_id').ids:
                            vals = {
                                'method_param_charac_id': conditional_method_param_charac_id._origin.id,
                                'from_parameter_characteristic_ids': True,
                                'is_conditional_parameter': True
                            }
                            self.line_ids += line_obj.new(vals)

            if not self.rel_regulation_id:
                self.analysis_id.regulation_id = self.method_param_charac_ids[0].regulation_id

        self.line_ids = self.line_ids.filtered('is_conditional_parameter') + \
                        self.line_ids.filtered(lambda line: not line.is_conditional_parameter)

    def create_results(self):
        """
        Results are already created => close window
        :return: dict
        """
        draft_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'draft')], limit=1)
        result_nu_ids = self.env['lims.analysis.numeric.result'].sudo()
        result_sel_ids = self.env['lims.analysis.sel.result'].sudo()
        result_ca_ids = self.env['lims.analysis.compute.result'].sudo()
        result_tx_ids = self.env['lims.analysis.text.result'].sudo()
        all_params = self.analysis_id.get_parameters()
        for line_id in self.line_ids.filtered(lambda l:
                                              not l.in_analysis and l.method_param_charac_id not in all_params):
            sop_id = self.analysis_id.mapped('sop_ids').filtered(
                lambda s: s.method_id == line_id.method_param_charac_id.method_id and s.rel_type != 'cancel')
            vals = {
                'analysis_id': self.analysis_id.id,
                'method_param_charac_id': line_id.method_param_charac_id.id,
                'pack_id': line_id.pack_id.id,
            }
            if sop_id:
                vals['sop_id'] = sop_id.id
            if not sop_id or sop_id.rel_type == 'draft':
                vals.update({
                    'stage_id': draft_stage_id.id,
                })

            result = False
            if line_id.method_param_charac_id.format == 'nu':
                result = result_nu_ids.create(vals)
                result_nu_ids += result
            elif line_id.method_param_charac_id.format == 'se':
                result = result_sel_ids.create(vals)
                result_sel_ids += result
            elif line_id.method_param_charac_id.format == 'ca':
                result = result_ca_ids.create(vals)
                result_ca_ids += result
            elif line_id.method_param_charac_id.format == 'tx':
                result = result_tx_ids.create(vals)
                result_tx_ids += result

            if result and not result.sop_id:
                self.analysis_id.create_sop()

        if result_nu_ids and result_nu_ids.filtered(lambda r: r.sop_id.rel_type != 'draft'):
            result_nu_ids.filtered(lambda r: r.sop_id.rel_type == 'plan').do_plan()
            result_nu_ids.filtered(lambda r: r.sop_id.rel_type not in ['draft', 'plan']).do_todo()
        if result_sel_ids and result_sel_ids.filtered(lambda r: r.sop_id.rel_type != 'draft'):
            result_sel_ids.filtered(lambda r: r.sop_id.rel_type == 'plan').do_plan()
            result_sel_ids.filtered(lambda r: r.sop_id.rel_type not in ['draft', 'plan']).do_todo()
        if result_ca_ids and result_ca_ids.filtered(lambda r: r.sop_id.rel_type != 'draft'):
            result_ca_ids.filtered(lambda r: r.sop_id.rel_type == 'plan').do_plan()
            result_ca_ids.filtered(lambda r: r.sop_id.rel_type not in ['draft', 'plan']).do_todo()
        if result_tx_ids and result_tx_ids.filtered(lambda r: r.sop_id.rel_type != 'draft'):
            result_tx_ids.filtered(lambda r: r.sop_id.rel_type == 'plan').do_plan()
            result_tx_ids.filtered(lambda r: r.sop_id.rel_type not in ['draft', 'plan']).do_todo()

        line_ids = self.line_ids.filtered(lambda l: not l.in_analysis)

        if self.parameter_pack_id and not self.parameter_pack_id.parameter_ids:
            self.analysis_id.pack_ids += self.parameter_pack_id
        if line_ids:
            pack_ids = line_ids.mapped('pack_id')
            for pack in pack_ids.filtered(lambda p: p not in self.analysis_id.pack_ids):
                self.analysis_id.pack_ids += pack
                self.analysis_id.message_post(body=_('New pack added: {}').format(pack.name))
            method_param_charac_ids = line_ids.filtered(lambda l: not l.pack_id).mapped('method_param_charac_id')
            for method_param_charac_id in method_param_charac_ids.filtered(lambda p: p not in self.analysis_id.method_param_charac_ids):
                self.analysis_id.method_param_charac_ids += method_param_charac_id
                self.analysis_id.message_post(body=_('New Parameter added: {}'.format(method_param_charac_id.name)))
            method_ids = line_ids.mapped('method_param_charac_id').mapped('method_id')
            self.analysis_id.mapped('sop_ids').filtered(lambda s: s.method_id in method_ids and s.rel_type and
                                                                  s.rel_type not in ['todo', 'cancel', 'draft', 'plan']).do_todo()
            if self.analysis_id.stage_id.type in ['done', 'validated1', 'validated2']:
                self.analysis_id.do_wip()


class AddParametersWizardLine(models.TransientModel):
    _name = 'add.parameters.wizard.line'
    _description = 'Add Parameter Line'

    add_parameters_wizard_id = fields.Many2one('add.parameters.wizard', ondelete='cascade')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter')
    pack_id = fields.Many2one('lims.parameter.pack', 'Pack')
    in_analysis = fields.Boolean()
    from_parameter_characteristic_ids = fields.Boolean()
    is_conditional_parameter = fields.Boolean()
