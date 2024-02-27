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
import datetime


class LimsSop(models.Model):
    _name = 'lims.sop'
    _description = 'Test'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, index=True)
    active = fields.Boolean('active', default=True)
    stage_id = fields.Many2one('lims.method.stage', string='Stage', tracking=True, index=True, copy=False,
                               domain="[('method_ids', '=', method_id)]")
    rel_type = fields.Selection(related='stage_id.type', readonly=True, store=True,
                                help="This is the 'Type' of the stage of that test.")
    method_id = fields.Many2one('lims.method', string='Method', index=True, readonly=True)
    department_id = fields.Many2one('lims.department', related='method_id.department_id', store=True,
                                    help="This is the 'Department' of the method of that test.")
    analysis_id = fields.Many2one('lims.analysis', string='Analysis', index=True, readonly=True, ondelete='cascade')
    result_num_ids = fields.One2many('lims.analysis.numeric.result', 'sop_id', 'Numerical Results')
    result_sel_ids = fields.One2many('lims.analysis.sel.result', 'sop_id', 'Selection Results')
    result_compute_ids = fields.One2many('lims.analysis.compute.result', 'sop_id', 'Computed result')
    result_text_ids = fields.One2many('lims.analysis.text.result', 'sop_id', 'Text result')
    labo_id = fields.Many2one('lims.laboratory', 'Labo', index=True, readonly=True)
    department_laboratory_id = fields.Many2one('lims.laboratory', string='Department Laboratory',
                                               related='department_id.labo_id', compute_sudo=True, readonly=True,
                                               help="This is the 'Laboratory' of the department of that test.")
    batch_id = fields.Many2one('lims.batch', string='Batch', index=True, readonly=True, tracking=True)
    date_plan = fields.Datetime('Date Plan', related='analysis_id.date_plan', store=True, readonly=True,
                                help="This is the 'Date plan' of the analysis that contain that test.")
    display_calendar = fields.Char(compute='get_display_name_calendar', compute_sudo=True)
    cancel_reason = fields.Char(tracking=True, copy=False)
    next_wip_stage = fields.Many2one('lims.method.stage', 'Next Stage', compute='compute_next_wip_stage', store=True)
    rel_partner_id = fields.Many2one('res.partner', related='analysis_id.partner_id', index=True, readonly=True,
                                     help="This is the 'Partner' of the analysis that contain that test.")
    rel_request_id = fields.Many2one('lims.analysis.request', related='analysis_id.request_id', index=True, store=True,
                                     help="This is the 'Request' of the analysis that contain that test.")
    rel_sample_name = fields.Char(string='Analysis Sample Name', related='analysis_id.sample_name', readonly=True,
                                  store=True, help="This is the 'Sample name' of the analysis that contain that test.")
    attribute_ids = fields.One2many('lims.method.attribute', 'sop_id')
    due_date = fields.Datetime('Due Date', index=True, readonly=True)
    rel_matrix_type_id = fields.Many2one(related='rel_matrix_id.type_id', store=True,
                                         help="This is the 'Type' of the matrix of the analysis that contain that test.")
    rel_matrix_id = fields.Many2one('lims.matrix', related="analysis_id.matrix_id", store=True,
                                    help="This is the 'Matrix' of the analysis that contain that test.")
    rel_regulation_id = fields.Many2one('lims.regulation', related="analysis_id.regulation_id",
                                        help="This is the 'Regulation' of the analysis that contain that test.")
    assigned_to = fields.Many2one('res.users', 'Assigned to', tracking=True)
    rel_time = fields.Float(related='method_id.time', store=True, help="This is the 'Time' of the method of that test.")
    rel_time_technician = fields.Float(related='method_id.time_technician', store=True,
                                       help="This is the 'Technician time' of the method of that test.")
    state = fields.Selection([('init', _('Init')), ('conform', _('Conform')), ('not_conform', _('Not Conform')),
                              ('unconclusive', _('Inconclusive'))], 'State', index=True, readonly=True, copy=False,
                             help="This is the state of the conformity of that test.")
    has_sample = fields.Boolean(tracking=True, string='Receptionned',
                                help="If this is not checked, the test will not be receptionned and will not be able "
                                     "to switch to the 'WIP' state.")
    display_info_subcontracted = fields.Boolean(compute='compute_display_info_subcontracted', compute_sudo=True,
                                                help="This is checked if the laboratory of that test is different "
                                                     "from the laboratory of his department.")
    is_ready = fields.Selection('get_value_is_ready', compute='compute_is_ready', store=True,
                                help="If the test is on stage 'WIP', this field will be also in 'WIP'. "
                                     "And if the test is on stage 'Validated', 'Done' or 'Cancel', this field will be 'Done'.  "
                                     "Otherwise, if amoung all the tests of his analysis who have a method in "
                                     "his child's methods ('method_ids'), then if one of them don't have "
                                     "the 'Is ready' field on 'Done', then this field will be 'Not ready'. "
                                     "In all other case, it will be 'Ready'.")
    comment = fields.Html('External comment',
                          help='Additional comment addressed to the customer (will be printed on analysis report)')
    note = fields.Text('Internal note',
                       help="Additional comment addressed to the internal team (won't be printed on analysis report)")
    is_duplicate = fields.Boolean(help="This is checked if the test was created by duplication.")
    parent_sop_id = fields.Many2one('lims.sop', string="Parent Test",
                                    help="This memorize the test that was used for duplication.")
    date_auto_cancel = fields.Datetime('Date Auto Annulation', readonly=True,
                                       help="Date when the test will be automatically canceled if the test is still in "
                                            "the ToDo state.")
    has_rework = fields.Boolean('Has rework', help='Test contains reworked results', tracking=True)
    product_id = fields.Many2one('product.product', 'Product', related='analysis_id.product_id', readonly=True,
                                 compute_sudo=True, store=True,
                                 help="This is the 'Product' of the analysis of that test.")
    rel_dept_user_ids = fields.Many2many('res.users', related="department_id.res_users_ids" , string="Dept User",
                                         help="This is the 'Users' of the department of that test.")
    rel_labo_users_ids = fields.Many2many('res.users', related="labo_id.res_users_ids", string="Lab User",
                                          help="This is the 'Users' of the laboratory of that test.")
    rel_work_instruction_id = fields.Many2one('lims.work.instruction', related='method_id.work_instruction_id', store=True,
                                              help="This is the 'Work instruction' of the method of that test.")

    @api.depends('analysis_id', 'analysis_id.sop_ids', 'analysis_id.sop_ids.stage_id', 'stage_id')
    def compute_is_ready(self):
        sop_ids = self.mapped('analysis_id.sop_ids').sudo()
        for sop_id in sop_ids:
            if sop_id.stage_id.type == 'wip':
                sop_id.is_ready = 'wip'
            elif sop_id.stage_id.type in ['validated', 'done', 'cancel']:
                sop_id.is_ready = 'done'
            elif sop_id.method_id.method_ids:
                sop_depend_ids = sop_id.analysis_id.sop_ids.filtered(
                    lambda s: s.method_id in sop_id.method_id.method_ids)
                if all(sop.is_ready == 'done' for sop in sop_depend_ids):
                    sop_id.is_ready = 'ready'
                else:
                    sop_id.is_ready = 'not_ready'
            else:
                sop_id.is_ready = 'ready'

    def get_value_is_ready(self):
        return [
            ('not_ready', _('Not Ready')),
            ('ready', _('Ready')),
            ('done', _('Done')),
            ('wip', _('WIP'))
        ]

    def compute_display_info_subcontracted(self):
        for record in self:
            if record.labo_id != record.department_laboratory_id:
                record.display_info_subcontracted = True
            else:
                record.display_info_subcontracted = False

    def check_sop_state(self):
        """
        Check the state of the analysis (conform, not conform, unconclusive) depends on the state of the results

        :return:
        """
        self = self.sudo()
        for record in self:
            record.get_result_conform_priority()
        self.analysis_id.check_analysis_state()

    def get_results(self):
        """
        retrieves all results in a list, does not depend on the type of result

        :return:
        """
        return list(self.result_num_ids) + list(self.result_sel_ids) + list(self.result_text_ids) + list(
            self.result_compute_ids)

    def get_results_filtered(self, stage=None, domain=None):
        """
        This function is used to get all result (prefilter)
        :param stage: Must be an iterable of string
        :param domain: Must be an 'lambda' function.
        :return:
        """
        if stage:
            domain = lambda r: r.rel_type in stage
        if domain:
            return list(self.result_num_ids.filtered(domain)) + list(
                self.result_compute_ids.filtered(domain)) + list(
                self.result_sel_ids.filtered(domain)) + list(
                self.result_text_ids.filtered(domain))
        return self.get_results()


    def get_result_conform_priority(self):
        """
        Check the state in the results of the analysis and return sop's state

        :return: sop's state
        """
        all_results = self.get_results_filtered(domain=lambda r: r.rel_type not in ['cancel', 'rework'])
        if any(r for r in all_results if r.state == 'not_conform'):
            self.state = 'not_conform'
        elif (self.labo_id.unconclusive_priority if self.labo_id else False) and any(
            r for r in all_results if r.state == 'unconclusive'):
            self.state = 'unconclusive'
        elif any(r for r in all_results if r.state in ['conform', 'unconclusive']):
            self.state = 'conform'
        elif any(r for r in all_results if r.state == 'init'):
            self.state = 'init'
        return self.state

    @api.depends('stage_id')
    def compute_next_wip_stage(self):
        next_wip_stage = self.env['lims.method.stage']
        wip_stages = next_wip_stage.sudo().search([('method_ids', 'in', self.method_id.ids), ('type', '=', 'wip')])
        for record in self:
            wip_stage = wip_stages.filtered(lambda x: record.method_id.id in x.method_ids.ids)
            if len(wip_stage) > 1 and record.stage_id.type == 'wip':
                is_next = False
                for wip in sorted(wip_stage, key=lambda stage: stage.sequence):
                    if is_next:
                        next_wip_stage = wip
                        break
                    if wip.id == record.stage_id.id:
                        is_next = True
            record.next_wip_stage = next_wip_stage

    @api.depends('name', 'method_id', 'analysis_id')
    def get_display_name_calendar(self):
        """
        Compute the display name for the view calendar
        :return:
        """
        for record in self:
            display_calendar = record.name
            if record.method_id and record.analysis_id:
                display_calendar = ' - '.join({display_calendar, record.method_id.name, record.analysis_id.name})
            record.display_calendar = display_calendar

    @api.onchange('method_id')
    def onchange_method_id(self):
        if self.method_id:
            param_obj = self.env['ir.config_parameter'].sudo()
            default_type_stage = param_obj.get_param('sop_stage_id', default='draft')
            method_stage = self.env['lims.method.stage'].sudo().search([('method_ids', '=', self.method_id.id),
                                                                        ('type', '=', default_type_stage)])
            if method_stage:
                self.stage_id = method_stage

    @api.model_create_multi
    def create(self, vals_list):
        """
        Get the name related to the sequence in the laboratory, else get the sequence for SOP
        Copy the attribute in method and set in sop
        :param vals:
        :return:
        """
        for vals in vals_list:
            if vals.get('labo_id'):
                labo = self.env['lims.laboratory'].browse(vals.get('labo_id'))
                if labo.seq_sop_id:
                    vals.update({
                        'name': labo.seq_sop_id.next_by_id()
                    })
                else:
                    raise exceptions.UserError(_('No sequence for the test in the laboratory'))
            else:
                vals.update({'name': self.env['ir.sequence'].get('lims.sop')})
            if vals.get('method_id') and not vals.get('stage_id'):
                param_obj = self.env['ir.config_parameter'].sudo()
                default_type_stage = param_obj.get_param('sop_stage_id', default='draft')
                method_stage = self.env['lims.method.stage'].sudo().search([
                    ('method_ids', '=', int(vals.get('method_id'))),
                    ('type', '=', default_type_stage)])
                if method_stage:
                    vals.update({
                        'stage_id': method_stage.id,
                    })
        res = super(LimsSop, self).create(vals_list)
        for sop in res.filtered(lambda s: s.method_id and s.method_id.attribute_ids):
            for attribute in sop.method_id.attribute_ids:
                sop.attribute_ids += attribute.copy({'sop_id': sop.id, 'method_id': False})
        return res

    def copy(self, default=None):
        """
        Copy the SOP with the result
        :param default:
        :return:
        """
        self.ensure_one()
        res = super(LimsSop, self).copy(default=default)
        draft_stage_id = self.env['lims.result.stage'].sudo().search([('type', '=', 'draft')])
        if not draft_stage_id:
            raise exceptions.ValidationError(_('No result stage "draft" found'))
        for result_id in self.result_num_ids.filtered(lambda r: r.rel_type != 'rework'):
            res.result_num_ids += result_id.copy(default={
                'analysis_id': res.analysis_id.id,
                'sop_id': res.id,
                'state': 'init',
                'value': 0,
                'is_null': False,
                'stage_id': draft_stage_id.id,
                'is_rework': False,
                'date_start': False,
                'show': res.analysis_id.laboratory_id.show_result_comment,
                'comment': False
            })
        for result_sel_id in self.result_sel_ids.filtered(lambda r: r.rel_type != 'rework'):
            res.result_sel_ids += result_sel_id.copy(default={
                'analysis_id': res.analysis_id.id,
                'sop_id': res.id,
                'state': 'init',
                'value_id': False,
                'stage_id': draft_stage_id.id,
                'date_start': False,
                'show': res.analysis_id.laboratory_id.show_result_comment,
                'comment': False
            })
        for compute_result_id in self.result_compute_ids.filtered(lambda r: r.rel_type != 'rework'):
            res.result_compute_ids += compute_result_id.copy(default={
                'analysis_id': res.analysis_id.id,
                'sop_id': res.id,
                'state': 'init',
                'stage_id': draft_stage_id.id,
                'date_start': False,
                'show': res.analysis_id.laboratory_id.show_result_comment,
                'comment': False
            })
        for result_text_id in self.result_text_ids.filtered(lambda r: r.rel_type != 'rework'):
            res.result_text_ids += result_text_id.copy(default={
                'analysis_id': res.analysis_id.id,
                'sop_id': res.id,
                'state': 'init',
                'stage_id': draft_stage_id.id,
                'date_start': False,
                'show': res.analysis_id.laboratory_id.show_result_comment,
                'comment': False
            })
        if res.rel_type == 'plan':
            if res.result_num_ids:
                res.result_num_ids.do_plan()
            if res.result_sel_ids:
                res.result_sel_ids.do_plan()
            if res.result_compute_ids:
                res.result_compute_ids.do_plan()
        elif res.rel_type != 'draft':
            if res.result_num_ids:
                res.result_num_ids.do_todo()
            if res.result_sel_ids:
                res.result_sel_ids.do_todo()
            if res.result_compute_ids:
                res.result_compute_ids.do_todo()
        return res

    def duplicate(self):
        self.ensure_one()
        duplicate_sop = self.copy()
        duplicate_sop.write({
            'is_duplicate': True,
            'parent_sop_id': self.id
        })

        analysis_stage = self.analysis_id.stage_id
        draft_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'draft')], limit=1)
        plan_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'plan')], limit=1)

        if analysis_stage.id == plan_stage_id.id:
            duplicate_sop.do_plan()
        elif analysis_stage.id not in [draft_stage_id.id, plan_stage_id.id]:
            duplicate_sop.do_todo()

        reason = self.env.context.get('reason', '')
        duplicate_sop.message_post(
            body=_("The SOP {0} has been duplicate from {1} with the following reason :\n {2}.".
                   format(duplicate_sop.name, self.name, reason))
        )

        return {
            'name': _('SOP'),
            'view_mode': 'form,tree,pivot,graph,calendar',
            'res_model': 'lims.sop',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': duplicate_sop.id,
        }

    def do_todo(self):
        """
        Pass the SOP in stage "todo", pass all the result in stage "todo"
        :return:
        """
        records = self
        if self.env.context.get('from_tree_view'):
            records = self.filtered(lambda s: s.stage_id.type in ['draft', 'plan', 'todo'])
        todo_stage_ids = self.env['lims.method.stage'].sudo().search([('method_ids', 'in', records.method_id.ids),
                                                                      ('type', '=', 'todo')])
        for record in records:
            todo_stage = todo_stage_ids.filtered(lambda s: record.method_id.id in s.method_ids.ids)
            record.stage_id = todo_stage and todo_stage[0].id
            now = fields.Datetime.now()
            if record.method_id and record.method_id.is_auto_cancel:
                if record.method_id.auto_cancel_time and 0 < record.method_id.auto_cancel_time:
                    delta = datetime.timedelta(hours=record.method_id.auto_cancel_time)
                    record.date_auto_cancel = now + delta

        result_ids = records.mapped('result_num_ids')
        result_sel_ids = records.mapped('result_sel_ids')
        compute_result_ids = records.mapped('result_compute_ids')
        result_text_ids = records.mapped('result_text_ids')
        analysis_ids = records.mapped('analysis_id')

        result_plan_state = self.env['lims.result.stage'].sudo().search([('type', '=', 'plan')], limit=1)
        result_todo_state = self.env['lims.result.stage'].sudo().search([('type', '=', 'todo')], limit=1)

        result_ids.filtered(lambda r: r.stage_id.type == 'draft').do_plan(result_plan_state)
        result_ids.filtered(lambda r: r.stage_id.type == 'plan').do_todo(result_todo_state)
        result_sel_ids.filtered(lambda r: r.stage_id.type == 'draft').do_plan(result_plan_state)
        result_sel_ids.filtered(lambda r: r.stage_id.type == 'plan').do_todo(result_todo_state)
        compute_result_ids.filtered(lambda r: r.stage_id.type == 'draft').do_plan(result_plan_state)
        compute_result_ids.filtered(lambda r: r.stage_id.type == 'plan').do_todo(result_todo_state)
        result_text_ids.filtered(lambda r: r.stage_id.type == 'draft').do_plan(result_plan_state)
        result_text_ids.filtered(lambda r: r.stage_id.type == 'plan').do_todo(result_todo_state)
        analysis_ids.filtered(lambda a: a.rel_type == 'draft').sudo().do_plan()
        analysis_ids.filtered(lambda a: a.rel_type == 'plan').sudo().do_todo()
        analysis_ids.filtered(lambda a: a.rel_type not in ['todo', 'cancel']).sudo().do_wip()
        records.batch_id.check_state()

    def do_cancel(self, cancel_reason=''):
        """
        Pass the SOP in stage "cancel", pass the all result in cancel, check state for batch, check state for analysis
        :param cancel_reason:
        :return:
        """
        result_cancel_state = self.env['lims.result.stage'].sudo().search([('type', '=', 'cancel')], limit=1)
        for record in self.filtered(lambda r: r.stage_id.type != 'cancel'):
            cancel_stage_id = self.env['lims.method.stage'].sudo().search([('method_ids', '=', record.method_id.id),
                                                                           ('type', '=', 'cancel')])
            if cancel_stage_id:
                record.write({
                    'stage_id': cancel_stage_id.id,
                    'cancel_reason': cancel_reason
                })
                record.result_compute_ids.filtered(
                    lambda r: r.rel_type not in ['cancel', 'rework']).do_cancel(result_cancel_state)
                record.result_num_ids.filtered(
                    lambda r: r.rel_type not in ['cancel', 'rework']).do_cancel(result_cancel_state)
                record.result_sel_ids.filtered(
                    lambda r: r.rel_type not in ['cancel', 'rework']).do_cancel(result_cancel_state)
                record.result_text_ids.filtered(
                    lambda r: r.rel_type not in ['cancel', 'rework']).do_cancel(result_cancel_state)
                record.batch_id.check_state()
                if record.analysis_id.stage_id.type != 'cancel':
                    record.analysis_id.check_state()

    def do_plan(self):
        """
        Pass the SOP in stage "plan", pass all the result in stage "plan"
        if action executed from tree view filter to pass only sop in stage 'draft'

        :return:
        """
        records = self
        if self.env.context.get('from_tree_view'):
            records = self.filtered(lambda s: s.stage_id.type == 'draft')
        plan_stage_dict = dict()
        for record in records:
            plan_stage_id = self.env['lims.method.stage'].sudo().search([('method_ids', '=', record.method_id.id),
                                                                         ('type', '=', 'plan')], limit=1)
            # PERF: Add in a variable to decrease number of database call
            if plan_stage_id:
                if not plan_stage_dict.get(plan_stage_id):
                    plan_stage_dict[plan_stage_id] = record
                else:
                    plan_stage_dict[plan_stage_id] += record
            else:
                raise exceptions.ValidationError(_('No method stage "plan" found'))

        # PERF: Write from variable to decrease number of database call
        for stage in plan_stage_dict:
            plan_stage_dict[stage].write({'stage_id': stage.id})
        stage_ids = self.env['lims.result.stage'].sudo().search([('type', 'in', ['draft', False])])
        result_plan_stage = self.env['lims.result.stage'].sudo().search([('type', '=', 'plan')], limit=1)
        # PERF: Done like this to decrease number of database call
        self.env['lims.analysis.numeric.result'].sudo().search([
            ('sop_id', 'in', records.ids), ('stage_id', 'in', stage_ids.ids)]).do_plan(result_plan_stage)
        self.env['lims.analysis.sel.result'].sudo().search([
            ('sop_id', 'in', records.ids), ('stage_id', 'in', stage_ids.ids)]).do_plan(result_plan_stage)
        self.env['lims.analysis.compute.result'].sudo().search([
            ('sop_id', 'in', records.ids), ('stage_id', 'in', stage_ids.ids)]).do_plan(result_plan_stage)
        self.env['lims.analysis.text.result'].sudo().search([
            ('sop_id', 'in', records.ids), ('stage_id', 'in', stage_ids.ids)]).do_plan(result_plan_stage)

    def do_wip(self):
        """
        Pass the SOP in stage "wip", pass all the result in stage "wip", pass the analysis in stage "wip"
        if action executed from tree view filter to pass only sop in stage 'draft', 'plan', 'todo'

        :return:
        """
        records = self
        if self.env.context.get('from_tree_view'):
            records = self.filtered(lambda s: s.stage_id.type in ['draft', 'plan', 'todo'])
            not_todo_records = records.filtered(lambda s: s.stage_id.type != 'todo')
            if not_todo_records:
                not_todo_records.do_todo()
        for record in records:
            wip_stage_id = self.env['lims.method.stage'].sudo().search([('method_ids', '=', record.method_id.id),
                                                                        ('type', '=', 'wip')], limit=1)
            if not wip_stage_id:
                raise exceptions.ValidationError(_('No method stage "wip" found'))
            if record.display_info_subcontracted and not record.has_sample:
                raise exceptions.ValidationError(_('The test must be receptionned {}').format(record.name))
            record.stage_id = wip_stage_id
        not_in_stage = ['cancel', 'rework', 'done', 'validated']
        result_wip_stage = self.env['lims.result.stage'].sudo().search([('type', '=', 'wip')], limit=1)
        records.result_num_ids.filtered(lambda r: r.rel_type not in not_in_stage).do_wip(result_wip_stage)
        records.result_compute_ids.filtered(lambda r: r.rel_type not in not_in_stage).do_wip(result_wip_stage)
        records.result_sel_ids.filtered(lambda r: r.rel_type not in not_in_stage).do_wip(result_wip_stage)
        records.result_text_ids.filtered(lambda r: r.rel_type not in not_in_stage).do_wip(result_wip_stage)
        records.mapped('analysis_id').sudo().do_wip()
        records.batch_id.check_state()

    def do_done(self):
        for record in self:
            done_stage_id = self.env['lims.method.stage'].sudo().search([('method_ids', '=', record.method_id.id),
                                                                         ('type', '=', 'done')], limit=1)
            if done_stage_id:
                record.stage_id = done_stage_id.id
                record.is_ready = 'done'
            else:
                raise exceptions.ValidationError(_('No method stage "done" found'))
        self.analysis_id.check_state()
        self.batch_id.check_state()

    def do_validated(self):
        sop_to_validate = self.filtered(lambda r: r.department_id in self.env.user.department_ids)
        if len(sop_to_validate) != len(self)  and not self.env.su:
            raise exceptions.ValidationError(_('You can not validated SOP from an another department : {}').format(
                ', '.join(sop.name for sop in self - sop_to_validate)
            ))
        if not self.user_has_groups('lims_base.self_sop_group'):
            result = self.result_num_ids.filtered(lambda line: not line.method_param_charac_id.auto_valid and line.user_id == self.env.user)
            if result:
                raise exceptions.ValidationError(_('You can not validated SOP you have filled'))

            result = self.result_sel_ids.filtered(lambda line: not line.method_param_charac_id.auto_valid and line.user_id == self.env.user)
            if result:
                raise exceptions.ValidationError(_('You can not validated SOP you have filled'))

            result = self.result_compute_ids.filtered(lambda line: not line.method_param_charac_id.auto_valid and line.user_id == self.env.user)
            if result:
                raise exceptions.ValidationError(_('You can not validated SOP you have filled'))
            result = self.result_text_ids.filtered(lambda line: not line.method_param_charac_id.auto_valid and line.user_id == self.env.user)
            if result:
                raise exceptions.ValidationError(_('You can not validated SOP you have filled'))
        validated_stage_ids = self.env['lims.method.stage'].sudo().search([('method_ids', 'in', self.method_id.ids),
                                                                          ('type', '=', 'validated')])
        for record in self:
            validated_stage_id = validated_stage_ids.filtered(lambda x: record.method_id.id in x.method_ids.ids)
            if validated_stage_id and len(validated_stage_id) == 1:
                record.stage_id = validated_stage_id.id
        if not self.env.context.get('from_result'):
            result_val_stage = self.env['lims.result.stage'].sudo().search([('type', '=', 'validated')], limit=1)
            self.result_num_ids.filtered(lambda r: r.rel_type == 'done').do_validated(result_val_stage)
            self.result_sel_ids.filtered(lambda r: r.rel_type == 'done').do_validated(result_val_stage)
            self.result_compute_ids.filtered(lambda r: r.rel_type == 'done').do_validated(result_val_stage)
            self.result_text_ids.filtered(lambda r: r.rel_type == 'done').do_validated(result_val_stage)
        self.analysis_id.check_state_validated()
        self.batch_id.check_state()

    def do_next_stage(self):
        if len(self.mapped('batch_id')) > 1:
            raise exceptions.UserError(_('You only can do this action for tests with the same batch'))
        elif self.filtered(lambda s: s.stage_id.type not in ['wip', 'todo']):
            raise exceptions.UserError(_('You only can do this actions to pass a test in wip stages'))
        record = self.filtered(lambda r: r.stage_id.type == 'todo')
        record.do_wip()
        record = self.filtered(lambda r: r.stage_id.type != 'todo')
        record.do_next_wip_stage()

    def check_do_cancel(self, cancel_stages):
        return self.result_num_ids and self.result_num_ids.filtered(lambda r: r.stage_id.id not in cancel_stages) or \
               self.result_sel_ids and self.result_sel_ids.filtered(lambda r: r.stage_id.id not in cancel_stages) or \
               self.result_text_ids and self.result_text_ids.filtered(lambda r: r.stage_id.id not in cancel_stages) or \
               self.result_compute_ids and self.result_compute_ids.filtered(
            lambda r: r.stage_id.id not in cancel_stages)

    def check_results_done(self):
        records = self.filtered(lambda r: r.stage_id.type != 'cancel')
        if records:
            result_done_stage = self.env['lims.result.stage'].sudo().search(
                [('type', 'in', ['done', 'validated'])])
            result_cancel_stage = self.env['lims.result.stage'].sudo().search(
                [('type', 'in', ['cancel', 'rework'])])
            done_stages = result_done_stage.ids + result_cancel_stage.ids
            cancel_stages = result_cancel_stage.ids
        for record in records.filtered(lambda r: not r.sudo().get_results_not_ok(done_stages)):
            do_cancel = record.sudo().check_do_cancel(cancel_stages)
            if not do_cancel:
                record.do_cancel()
            else:
                record.do_done()

    def check_state_validated(self):
        stage_ids = self.env['lims.result.stage'].sudo().search([('type', 'in', ['validated', 'rework', 'cancel'])])
        sop_to_validate = self.filtered(lambda r: not r.sudo().get_results_not_ok(stage_ids.ids) and \
                                                  r.stage_id.type != 'validated')
        if sop_to_validate:
            sop_to_validate.with_context(from_result=True).do_validated()

    def get_results_not_ok(self, stage_ids):
        self.ensure_one()
        not_ok = self.result_num_ids and self.result_num_ids.filtered(lambda r: r.stage_id.id not in stage_ids) or \
                 self.result_sel_ids and self.result_sel_ids.filtered(lambda r: r.stage_id.id not in stage_ids) or \
                 self.result_text_ids and self.result_text_ids.filtered(lambda r: r.stage_id.id not in stage_ids) or \
                 self.result_compute_ids and self.result_compute_ids.filtered(lambda r: r.stage_id.id not in stage_ids)
        return not_ok

    def unlink(self):
        batch_ids = self.mapped('batch_id')
        analysis_ids = self.mapped('analysis_id')
        res = super(LimsSop, self).unlink()
        analysis_ids.check_analysis_state()
        batch_ids.check_state()
        analysis_ids.check_state()
        return res

    def do_next_wip_stage(self):
        for record in self.filtered(lambda r: r.next_wip_stage):
            record.stage_id = record.next_wip_stage.id

    def do_is_null(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('lims_base.do_sop_is_null_wizard_action')
        return action

    def do_create_batch(self, batch=False):
        batch = self.create_batch(batch=batch)
        return {
            'name': _("Batch"),
            'view_mode': 'form',
            'view_id': self.env.ref('lims_base.lims_batch_form_view').id,
            'res_model': 'lims.batch',
            'res_id': batch.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def create_batch(self, batch=False):
        batch_obj = self.env['lims.batch']
        if self.filtered(lambda s: not s.method_id):
            raise exceptions.UserError(_('There is no method in the test'))
        if self.filtered(lambda s: s.rel_type not in ('draft', 'todo', 'plan')):
            raise exceptions.UserError(
                _('You can only create batch from test in state \'draft\' or \'todo\' or \'plan\''))
        if len(set(self.mapped('rel_type'))) != 1:
            raise exceptions.ValidationError(_('You can\'t have different states between the selected tests'))
        if self.filtered(lambda s: s.batch_id):
            raise exceptions.ValidationError(_('Some tests are already in a batch'))
        if len(self.mapped('labo_id')) != 1 or len(self.mapped('department_id')) != 1:
            raise exceptions.UserError(_('You can create batch only if laboratory and department are the same'))
        if batch:
            if batch.rel_labo_id != self[0].labo_id or batch.rel_department_id != self[0].department_id:
                raise exceptions.UserError(
                    _('You can modify batch only if they have the same laboratory and department of the test(s)')
                )
            batch.method_ids = [(4, method_id.id) for method_id in self.mapped('method_id')]
            batch.sop_ids = [(4, sop_id.id) for sop_id in self]
        else:
            batch_values = {
                'method_ids': [(4, method_id.id) for method_id in self.mapped('method_id')],
                'sop_ids': [(4, sop_id.id) for sop_id in self],
                'rel_labo_id': self[0].labo_id.id,
                'rel_department_id': self[0].department_id.id,
            }
            batch = batch_obj.create(batch_values)
            batch.check_state()
        return batch


    def do_open_wizard_cancel(self):
        context = self.env.context.copy()
        context.update({
            'default_sop_ids': self.ids,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sop.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def do_open_wizard_rework(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'default_sop_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sop.rework.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def sop_duplicate_reason_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sop.duplicate.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sop_id': self.id
            },
        }

    def name_get(self):
        context = self.env.context
        if context.get('params') and context['params'].get('view_type') == 'calendar':
            calendar_res = []
            for record in self:
                calendar_res.append((record.id, record.name + " -- " + record.method_id.name))
            return calendar_res
        res = super(LimsSop, self).name_get()
        return res

    @api.model
    def check_sop_expired_date_auto_cancel(self):
        all_sop_ids = self.env['lims.sop'].search([('rel_type', '=', 'todo'), ('date_auto_cancel', '!=', False)])
        for sop_id in all_sop_ids:
            if sop_id.date_auto_cancel < fields.Datetime.now():
                sop_id.do_cancel(cancel_reason=_("The test remained in ToDo state after the auto cancellation date."))
                date_with_fz = fields.Datetime.context_timestamp(self, sop_id.date_auto_cancel)
                sop_id.message_post(body=_("This test was automatically canceled, because the test remained in ToDo "
                                           "state after the auto cancellation date. Date auto cancel : {}".
                                           format(datetime.datetime.strftime(date_with_fz, '%d/%m/%Y %H:%M:%S'))))

    def assign_test_to_self(self):
        """
        Assigns the test to the user

        if action executed from tree view filter to assign only sop in stage 'draft', 'plan', 'todo'
        and not yet assigned

        :return:
        """
        records = self
        if self.env.context.get('from_tree_view'):
            records = self.filtered(lambda t: t.stage_id.type in ['draft', 'plan', 'todo'] and not t.assigned_to)
        records.assigned_to = records.env.user

    def archive_cascade(self):
        """
        Toggle active for sop and result
        :return:
        """
        for record in self:
            record.toggle_active()
            record.result_num_ids.toggle_active()
            record.result_compute_ids.toggle_active()
            record.result_sel_ids.toggle_active()
            record.result_text_ids.toggle_active()

    def get_all_params(self):
        def stage_cond(result):
            return result.filtered(lambda r: r.rel_type != 'cancel' or r.rel_type != 'rework')

        self.ensure_one()
        return stage_cond(self.result_num_ids).method_param_charac_id + \
            stage_cond(self.result_compute_ids).method_param_charac_id + \
            stage_cond(self.result_sel_ids).method_param_charac_id + \
            stage_cond(self.result_text_ids).method_param_charac_id
