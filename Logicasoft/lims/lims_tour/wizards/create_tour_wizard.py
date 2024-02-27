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
from odoo import fields, models, api, _


class CreateTourWizard(models.TransientModel):
    # this wizard is called from lims.analysis view
    _name = 'create.tour.wizard'
    _description = 'Create Tour Wizard'

    def get_default_laboratory(self):
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    analysis_ids = fields.Many2many('lims.analysis')
    tour_id = fields.Many2one('lims.tour')
    date = fields.Datetime('Date')
    state = fields.Selection('get_state_selection', 'State', default='plan')
    note = fields.Text('Note')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', default=get_default_laboratory)
    sampler_id = fields.Many2one('hr.employee.public', 'Sampler')
    tour_line_ids = fields.One2many('lims.tour.line', 'tour_id', 'Lines')
    sampler_team_id = fields.Many2one('lims.sampler.team', 'Sampler Team')
    rel_sampler_ids = fields.Many2many('hr.employee.public', related='sampler_team_id.sampler_ids',
                                       string="Team's sampler")

    @api.model
    def get_state_selection(self):
        return [
            ('plan', _('Plan')),
            ('todo', _('To Do')),
            ('wip', _('WIP')),
            ('done', _('Done')),
            ('cancel', _('Cancel')),
        ]

    def do_create_add_tour(self):
        if self.tour_id:
            tour = self.add_tour()
        else:
            tour = self.create_tour()
        form = self.env.ref('lims_tour.lims_tour_form')
        action = self.env['ir.actions.act_window']._for_xml_id('lims_tour.lims_tour_action')
        action.update({
            'view_mode': 'form',
            'view_id': form.id,
            'res_id': tour.id,
        })
        return action

    def add_tour(self):
        analysis_with_tour_line_ids = self.analysis_ids.filtered('tour_id')
        analysis_with_tour_line_ids.write({
            'tour_id': self.tour_id.id,
            'sampler_id': self.tour_id.sampler_id and self.tour_id.sampler_id.id or False,
        })
        analysis_without_tour_line_ids = self.analysis_ids.filtered(
            lambda a: a not in analysis_with_tour_line_ids)
        tour_line_obj = self.env['lims.tour.line']
        for analysis_id in analysis_without_tour_line_ids:
            tour_line_obj.create({
                'tour_id': self.tour_id.id,
                'analysis_id': analysis_id.id,
                'sampler_id': self.sampler_id and self.sampler_id.id or False,
            })
        analysis_without_tour_line_ids.write({
            'tour_id': self.tour_id.id,
            'sampler_id': self.tour_id.sampler_id and self.tour_id.sampler_id.id or False,
        })

        return self.tour_id

    def create_tour(self):
        tour_obj = self.env['lims.tour']
        tour_line_obj = self.env['lims.tour.line']
        vals = {
            'name': self.laboratory_id.seq_tour_id and self.laboratory_id.seq_tour_id.next_by_id() or '/',
            'date': self.date,
            'state': 'plan',
            'note': self.note,
            'laboratory_id': self.laboratory_id and self.laboratory_id.id,
            'sampler_id': self.sampler_id and self.sampler_id.id or False,
            'sampler_team_id': self.sampler_team_id and self.sampler_team_id.id or False,
        }
        tour_id = tour_obj.create(vals)
        for analysis_id in self.analysis_ids:
            if analysis_id.tour_id:
                analysis_id.write({
                    'tour_id': tour_id.id,
                    'sampler_id': self.sampler_id and self.sampler_id.id or False,
                })
            else:
                tour_line_obj.create({
                    'tour_id': tour_id.id,
                    'analysis_id': analysis_id.id,
                    'sampler_id': self.sampler_id and self.sampler_id.id or False,
                    })
        return tour_id
