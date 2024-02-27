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
from odoo import fields, models, api, _, exceptions


class LimsBatch(models.Model):
    _name = 'lims.batch'
    _description = 'Batch'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    name = fields.Char('Name', required=True, index=True, tracking=True)
    description = fields.Text('Description', tracking=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, index=True, tracking=True)
    sop_ids = fields.One2many('lims.sop', 'batch_id', 'Test', tracking=True)
    method_ids = fields.Many2many('lims.method', string='Method', compute='compute_method_ids', store=True,
                                  help="It's the methods of the tests.")
    nb_sop = fields.Integer('NB Test', compute='compute_nb_sop')
    nb_result = fields.Integer('NB NU', compute='compute_nb_result')
    nb_sel_result = fields.Integer('NB SE', compute='compute_nb_sel_result')
    nb_compute_result = fields.Integer('NB CA', compute='compute_nb_compute_result')
    nb_text_result = fields.Integer('NB TX', compute='compute_nb_text_result')
    operator_ids = fields.One2many('lims.batch.operator', 'batch_id', string='Operator')
    rel_labo_id = fields.Many2one('lims.laboratory', 'Laboratory', default=get_default_laboratory, tracking=True)
    rel_department_id = fields.Many2one('lims.department', 'Department', tracking=True)
    display_calendar = fields.Char(compute='get_display_name_calendar')
    state = fields.Selection('get_state_selection', default='draft', tracking=True, index=True)
    assigned_to = fields.Many2one('res.users', 'Assigned to', tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    is_cancel = fields.Boolean('Cancelled', tracking=True,
                               help="This is checked when the batch switch to 'Cancel' state.")

    def get_state_selection(self):
        """
        Return different state for the batch
        :return: list of tuple
        """
        return [
            ('draft', _('Draft')),
            ('plan', _('Plan')),
            ('todo', _('ToDo')),
            ('wip', _('WIP')),
            ('done', _('Done')),
            ('validated', _('Validated')),
            ('cancel', _('Cancelled')),
        ]

    @api.depends('name', 'method_ids')
    def get_display_name_calendar(self):
        """
        Compute the display name in the view calendar
        :return:
        """
        for record in self:
            display_calendar = record.name
            if record.method_ids:
                display_calendar = display_calendar + ' - ' + record.method_ids.mapped('name')[0]
            record.display_calendar = display_calendar

    @api.depends('sop_ids', 'sop_ids.method_id')
    def compute_method_ids(self):
        for record in self:
            record.method_ids = [(4, method_id.id) for method_id in record.sop_ids.mapped('method_id')]

    def open_batch_sop(self):
        """
        Open view SOP related to this batch
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Test',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.sop',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'context': {'default_batch_id': self.id,
                        'search_default_batch_id': self.id,
                        },
        }

    def open_batch_result(self):
        """
        Open view SOP related to this batch
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.numeric.result',
            'view_mode': 'tree,graph,pivot,calendar',
            'context': {'search_default_rel_batch_id': self.id},
        }

    def open_batch_sel_result(self):
        """
        Open view SOP related to this batch
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Sel result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.sel.result',
            'view_mode': 'tree,calendar',
            'context': {'search_default_rel_batch_id': self.id},
        }

    def open_batch_compute_result(self):
        """
        Open view SOP related to this batch
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Compute result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.compute.result',
            'view_mode': 'tree,calendar',
            'context': {'search_default_rel_batch_id': self.id},
        }

    def open_batch_text_result(self):
        """
        Open view SOP related to this batch
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Text result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.text.result',
            'view_mode': 'tree,calendar',
            'context': {'search_default_rel_batch_id': self.id},
        }

    def compute_nb_sop(self):
        """
        Compute the number of SOP for this batch
        :return:
        """
        for record in self:
            record.nb_sop = len(record.sop_ids)

    @api.constrains('sop_ids', 'rel_department_id', 'rel_labo_id')
    def check_sop_ids(self):
        if self.filtered(lambda r: len(r.sop_ids.mapped('department_id')) > 1 or len(r.sop_ids.mapped('labo_id')) > 1):
            raise exceptions.ValidationError(_('Laboratory and department of tests must be the same than laboratory '
                                               'and department of batch'))

    def compute_nb_result(self):
        """
        Compute the number of result for this batch
        :return:
        """
        if self.ids:
            counted_data = self.env['lims.analysis.numeric.result'].read_group([('rel_batch_id', 'in', self.ids)],
                                                                               ['rel_batch_id'], ['rel_batch_id'])
            mapped_data = { count['rel_batch_id'][0]: count['rel_batch_id_count'] for count in counted_data }
        else:
            mapped_data = {}

        for record in self:
            record.nb_result = mapped_data.get(record.id, 0)

    def compute_nb_sel_result(self):
        """
        Compute the number of selection result for this batch
        :return:
        """
        if self.ids:
            counted_data = self.env['lims.analysis.sel.result'].read_group([('rel_batch_id', 'in', self.ids)],
                                                                           ['rel_batch_id'], ['rel_batch_id'])
            mapped_data = { count['rel_batch_id'][0]: count['rel_batch_id_count'] for count in counted_data }
        else:
            mapped_data = {}

        for record in self:
            record.nb_sel_result = mapped_data.get(record.id, 0)

    def compute_nb_compute_result(self):
        """
        Compute the number of compute result for this batch
        :return:
        """
        if self.ids:
            counted_data = self.env['lims.analysis.compute.result'].read_group([('rel_batch_id', 'in', self.ids)],
                                                                               ['rel_batch_id'], ['rel_batch_id'])
            mapped_data = { count['rel_batch_id'][0]: count['rel_batch_id_count'] for count in counted_data }
        else:
            mapped_data = {}

        for record in self:
            record.nb_compute_result = mapped_data.get(record.id, 0)

    def compute_nb_text_result(self):
        """
        Compute the number of text result for this batch
        :return:
        """
        if self.ids:
            counted_data = self.env['lims.analysis.text.result'].read_group([('rel_batch_id', 'in', self.ids)],
                                                                            ['rel_batch_id'], ['rel_batch_id'])
            mapped_data = { count['rel_batch_id'][0]: count['rel_batch_id_count'] for count in counted_data }
        else:
            mapped_data = {}

        for record in self:
            record.nb_text_result = mapped_data.get(record.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Set the name depends on the sequence in method_id, create the record
        :param vals:
        :return:
        """
        for vals in vals_list:
            if vals.get('rel_labo_id'):
                labo = self.env['lims.laboratory'].browse(int(vals.get('rel_labo_id')))
                if not labo:
                    raise exceptions.UserError(_('There is no laboratory in the method'))
                vals.update({'name': labo.seq_batch_id.next_by_id()})
        return super(LimsBatch, self).create(vals_list)

    def do_draft(self):
        """
        Pass the batch in state "draft"
        :return:
        """
        self.write({
            'state': 'draft',
        })

    def do_plan(self):
        self.write({
            'state': 'plan',
        })

    def do_todo(self):
        self.write({
            'state': 'todo',
        })

    def do_wip(self):
        """
        Pass the batch in state "wip"
        :return:
        """
        self.write({
            'state': 'wip',
        })

    def do_done(self):
        """
        Pass the batch in state "done"
        :return:
        """
        self.write({
            'state': 'done',
        })

    def do_validated(self):
        self.write({
            'state': 'validated',
        })

    def do_cancel(self):
        """
        Pass the batch in state "cancel"
        :return:
        """
        self.write({
            'state': 'cancel',
            'is_cancel': True,
        })

    def check_state(self):
        """
        Check the batch's state.
        :return:
        """
        for record in self.filtered(lambda b: not b.is_cancel):
            state_list = set(record.sop_ids.mapped('rel_type'))
            if state_list == {'cancel'}:
                if record.state != 'cancel':
                    record.state = 'cancel'
            elif not (state_list - {'validated', 'cancel'}):
                if record.state != 'validated':
                    record.do_validated()
            elif not (state_list - {'done', 'validated', 'cancel'}):
                if record.state != 'done':
                    record.do_done()
            elif state_list - {'draft', 'plan', 'todo', 'cancel'}:
                if record.state != 'wip':
                    record.do_wip()
            elif state_list - {'draft', 'plan', 'cancel'}:
                if record.state != 'todo':
                    record.do_todo()
            elif state_list - {'draft', 'cancel'}:
                if record.state != 'plan':
                    record.do_plan()
            elif state_list == {'draft'}:
                if record.state != 'draft':
                    record.do_draft()
