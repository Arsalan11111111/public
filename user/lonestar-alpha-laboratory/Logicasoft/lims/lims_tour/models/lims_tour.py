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


class LimsTour(models.Model):
    _name = 'lims.tour'
    _description = 'Lims Tour'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date desc, id'

    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        if 'laboratory_id' in default_fields and values.get('laboratory_id') is None:
            laboratory_id = self.env.user.default_laboratory_id or self.env[
                'lims.laboratory'].search([('default_laboratory', '=', True)])
            values['laboratory_id'] = laboratory_id.id
        return values

    display_name = fields.Char('Display Name', compute='get_rec_name', store=True)
    name = fields.Char('Name', tracking=True, default='/')
    date = fields.Datetime('Date', tracking=True)
    state = fields.Selection('get_state_selection', 'State', default='plan', tracking=True)
    note = fields.Text('Note')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', tracking=True)
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler', tracking=True)
    tour_line_ids = fields.One2many('lims.tour.line', 'tour_id', 'Lines', tracking=True)
    sampler_team_id = fields.Many2one('lims.sampler.team', 'Sampler Team', tracking=True)
    rel_sampler_ids = fields.Many2many('hr.employee.public', related='sampler_team_id.sampler_ids',
                                       string="Team's sampler")
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium (*)'), ('3', 'High (**)'), ('4', 'Highest (***)')],
                                tracking=True)
    is_expired = fields.Boolean(compute='compute_is_expired')
    display_calendar = fields.Char(compute='get_display_name_calendar')
    is_model = fields.Boolean('Is Model', copy=False, tracking=True)
    tour_name_id = fields.Many2one('lims.tour.name', tracking=True)
    nb_sop = fields.Integer('Tests', compute='get_nb_sop')
    nb_analysis = fields.Integer('Analysis', compute='get_nb_analysis')
    nb_result = fields.Integer('NU', compute='get_nb_result')
    nb_ca_result = fields.Integer('CA', compute='get_nb_ca_result')
    nb_sel_result = fields.Integer('SE', compute='get_nb_sel_result')
    nb_text_result = fields.Integer('TX', compute='get_nb_text_result')

    @api.depends('name')
    def get_rec_name(self):
        for record in self:
            record.display_name = record.name
            if record.tour_name_id:
                record.display_name += ": {}".format(record.tour_name_id.name)

    def get_nb_sop(self):
        for record in self:
            record.nb_sop = self.env['lims.sop'].search_count([('tour_id', '=', record.id)])

    def get_nb_analysis(self):
        for record in self:
            record.nb_analysis = self.env['lims.analysis'].search_count([('tour_id', '=', record.id)])

    def get_nb_result(self):
        for record in self:
            record.nb_result = self.env['lims.analysis.numeric.result'].search_count([('tour_id', '=', record.id)])

    def get_nb_ca_result(self):
        for record in self:
            record.nb_ca_result = self.env['lims.analysis.compute.result'].search_count([('tour_id', '=', record.id)])

    def get_nb_sel_result(self):
        for record in self:
            record.nb_sel_result = self.env['lims.analysis.sel.result'].search_count([('tour_id', '=', record.id)])

    def get_nb_text_result(self):
        for record in self:
            record.nb_text_result = self.env['lims.analysis.text.result'].search_count([('tour_id', '=', record.id)])

    def write(self, vals):
        if self.env.context.get('force_write') or self.env.context.get('install_mode'):
            return super(LimsTour, self).write(vals)
        if self.filtered(lambda r: r.is_model) and 'is_model' not in vals:
            raise exceptions.ValidationError(_('You can not modify a model tour'))
        if vals.get('date') and self.filtered(lambda r: r.state in ['wip', 'done', 'cancel']):
            raise exceptions.ValidationError(_('You can not modify the date if the tour is cancelled or wip or done'))
        res = super(LimsTour, self).write(vals)
        if vals.get('date') and self.mapped('tour_line_ids').mapped('analysis_id'):
            self.mapped('tour_line_ids').mapped('analysis_id').write({
                'date_plan': vals.get('date')
            })
        if 'sampler_id' in vals:
            self.mapped('tour_line_ids').mapped('analysis_id').write({
                'sampler_id': vals['sampler_id']
            })
        return res

    def copy(self, default=None):
        """
        Copy tour, if copy_all is in context, then copy analysis,sop,sample
        :param default:
        :return:
        """
        self.ensure_one()
        if self.env.context.get('copy_all'):
            copy_tour = super(LimsTour, self).copy(default)
            for tour_line_id in self.tour_line_ids:
                vals = tour_line_id.analysis_id.get_vals_for_recurrence()
                vals['date_plan'] = copy_tour.date
                vals['tour_id'] = copy_tour.id
                copy_analyse = tour_line_id.analysis_id.copy(default=vals)
                tour_line_id.copy(default={'tour_id': copy_tour.id,
                                           'time_float': 0,
                                           'analysis_id': copy_analyse.id,
                                           'color_on_line': False})
            return copy_tour
        return super(LimsTour, self).copy(default)

    def print_container(self):
        """
        Print containers
        :return:
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'print.qweb.container.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_analysis_ids': self.tour_line_ids.mapped('analysis_id').ids}
        }

    def print_label(self):
        """
        Print the labels
        :return:
        """
        if self.tour_line_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'print.qweb.label.wizard',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'target': 'new',
                'context': {'default_analysis_ids': self.tour_line_ids.mapped('analysis_id').ids}
            }

    @api.depends('name', 'tour_name_id', 'sampler_id', 'priority')
    def get_display_name_calendar(self):
        """
        Compute the dispay name for the view calendar
        :return:
        """
        for record in self:
            display_calendar = record.name
            if record.tour_name_id:
                display_calendar = display_calendar + ' - ' + record.tour_name_id.name
            if record.sampler_id:
                display_calendar = display_calendar + ' - ' + record.sampler_id.name
            if record.priority:
                display_calendar += ' - '
                if record.priority == 1:
                    display_calendar += '*'
                elif record.priority == 2:
                    display_calendar += '**'
                else:
                    display_calendar += '***'
            record.display_calendar = display_calendar

    def compute_is_expired(self):
        """
        Compute if the tour is out or not
        :return:
        """
        for record in self:
            record.is_expired = bool(record.date and record.date < fields.Datetime.now())

    @api.model_create_multi
    def create(self, vals_list):
        """
        When create tour, get the name from the ir sequence
        :param vals:
        :return:
        """
        for vals in vals_list:
            if vals.get('name', '/') == '/' and vals.get('laboratory_id'):
                labo = self.env['lims.laboratory'].search([('id', '=', vals.get('laboratory_id'))])
                if labo.seq_tour_id:
                    vals.update({'name': labo.seq_tour_id.next_by_id()})
        return super().create(vals_list)

    @api.model
    def get_state_selection(self):
        """
        Get all state possible for tour
        :return: dictionnary of tuple
        """
        return [
            ('plan', _('Plan')),
            ('todo', _('To Do')),
            ('wip', _('WIP')),
            ('done', _('Done')),
            ('cancel', _('Cancelled')),
        ]

    def do_to_do(self):
        """
        Set state todo
        :return:
        """
        self.write({'state': 'todo'})
        if self.tour_line_ids and self.tour_line_ids.mapped('analysis_id'):
            analysis_ids = self.tour_line_ids.mapped('analysis_id').filtered(lambda a: a.stage_id.type == 'draft')
            if analysis_ids:
                analysis_ids.do_plan()

    def do_wip(self):
        """
        Set state wip
        :return:
        """
        self.write({'state': 'wip'})

    def do_done(self):
        """
        Set state done , set date_sample (is no date_sample is set) and the sampler in the analysis
        :return:
        """
        for record in self:
            analysis = record.mapped('tour_line_ids').mapped('analysis_id')
            analysis.filtered(lambda a: not a.sampler_id).with_context(force_write=True).write(
                {'sampler_id': record.sampler_id.id})
            analysis.filtered(lambda a: not a.date_sample).with_context(force_write=True).write(
                {'date_sample': fields.Datetime.now()})
        self.write({'state': 'done'})

    def do_cancel(self, comment=''):
        """
        Set state cancel
        :return:
        """
        self.write({'state': 'cancel'})
        self.message_post(body=_('Tour cancelled reason: {} by {}'.format(comment, self.env.user.name)))

    def open_wizard_cancel(self):
        return {
            'name': _('Cancel Tour'),
            'type': 'ir.actions.act_window',
            'res_model': 'tour.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def do_reset_todo(self):
        self.ensure_one()
        self.write({
            'state': 'todo'
        })

    def do_reset(self):
        """
        Set state plan and remove the date
        :return:
        """
        self.with_context(force_write=True).write({'state': 'plan', 'date': False})
        self.message_post(body=_('Tour reset by {}'.format(self.env.user.name)))

    def open_tour_sop(self):
        """
        Open view for SOP (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Test',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.sop',
            'view_mode': 'tree,form',
            'context': {'search_default_tour_id': self.id},
        }

    def open_tour_analysis(self):
        """
        Open view for Analysis (used in smart button)
        :return:
        """
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('lims_tour.lims_tour_line_action')
        action['context'] = {'search_default_tour_id': self.id, 'create': False, 'update_from_tour_line': True}
        return action

    def open_tour_line_map(self):
        """
        Open view for tour line (used to open map)
        :return:
        """
        self.ensure_one()
        action = self.open_tour_analysis().copy()
        action['display_name'] = _('Map [{}]').format(self.display_name)
        views = action.get('views')
        for element in action.get('views'):
            if element[1] == 'map':
                views.insert(0, views.pop(views.index(element)))
                break
        action['views'] = views
        action['domain'] = [('tour_id', '=', self.id)]
        action['context'] = {'search_default_tour_id': self.id, 'search_default_group_by_is_on_site_complete': 1,
                             'update_from_tour_line': True}
        return action

    def open_tour_result(self):
        """
        Open view for Analysis results (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Analysis result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.numeric.result',
            'view_mode': 'tree,graph,pivot,calendar',
            'context': {'search_default_tour_id': self.id,
                        'default_tour_id': self.id},
        }

    def open_tour_ca_result(self):
        """
        Open view for Analysis results (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Analysis compute result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.compute.result',
            'view_mode': 'tree,graph,pivot',
            'context': {'search_default_tour_id': self.id,
                        'default_tour_id': self.id},
        }

    def open_tour_sel_result(self):
        """
        Open view for Analysis selection results (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Analysis selection result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.sel.result',
            'view_mode': 'tree,calendar',
            'context': {'search_default_tour_id': self.id,
                        'default_tour_id': self.id},
        }

    def open_tour_text_result(self):
        """
        Open view for Analysis text results (used in smart button)
        :return:
        """
        self.ensure_one()
        return {
            'name': 'Analysis text result',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.text.result',
            'view_mode': 'tree,calendar',
            'context': {'search_default_tour_id': self.id,
                        'default_tour_id': self.id},
        }

    def get_analysis(self):
        self.ensure_one()
        analysis_ids = self.env['lims.tour.line'].search([('tour_id', '=', self.id)])
        return analysis_ids

    def _compute_access_url(self):
        super()._compute_access_url()
        for tour in self:
            tour.access_url = f'/my/tours/{tour.id}'
