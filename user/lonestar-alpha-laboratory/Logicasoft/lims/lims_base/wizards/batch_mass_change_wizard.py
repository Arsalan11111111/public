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
from odoo import models, fields, api, _, exceptions


def get_state(self):
    return [
        ('draft', _('Draft')),
        ('wip', _('WIP')),
        ('done', _('Done')),
        ('cancel', _('Cancelled')),
    ]


class SopMassChangeWizard(models.TransientModel):
    _name = 'batch.mass.change.wizard'
    _description = 'Batch Mass Change'

    line_ids = fields.One2many('batch.mass.change.wizard.line', 'wizard_id')
    state = fields.Selection(get_state)
    assigned_to = fields.Many2one('res.users', 'Assigned to')
    date = fields.Datetime('Date')

    @api.model
    def default_get(self, fields_list):
        res = super(SopMassChangeWizard, self).default_get(fields_list)
        line_ids = []
        for batch in self.env.context.get('active_ids', []):
            batch_id = self.env['lims.batch'].browse(batch)
            line_ids.append((0, 0, {
                'batch_id': batch_id.id,
                'assigned_to': batch_id.assigned_to.id,
                'state': batch_id.state,
                'date': batch_id.date,
            }))
        res.update({'line_ids': line_ids})
        return res

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            for line_id in self.line_ids:
                line_id.date = self.date

    @api.onchange('state')
    def onchange_state(self):
        if self.state:
            for line_id in self.line_ids:
                line_id.state = self.state

    @api.onchange('assigned_to')
    def onchange_assigned_to(self):
        if self.assigned_to:
            self.line_ids.update({'assigned_to': self.assigned_to.id})

    def do_confirm(self):
        states = self.line_ids.mapped('state')
        for state in states:
            batch_ids = self.line_ids.filtered(lambda l: l.state == state).mapped('batch_id')
            if state == 'draft':
                batch_ids.do_draft()
            elif state == 'wip':
                batch_ids.do_wip()
            elif state == 'done':
                batch_ids.do_done()
            elif state == 'cancel':
                batch_ids.do_cancel()
        values = self.line_ids.mapped('assigned_to')
        for user in values:
            self.line_ids.filtered(lambda l: l.assigned_to == user).mapped('batch_id').write({
                'assigned_to': user.id
            })
        values = self.line_ids.mapped('date')
        for value in values:
            self.line_ids.filtered(lambda l: l.date == value).mapped('batch_id').write({
                'date': value
            })


class BatchMassChangeWizardLine(models.TransientModel):
    _name = 'batch.mass.change.wizard.line'
    _description = 'Batch Mass Change Line'

    wizard_id = fields.Many2one('batch.mass.change.wizard')
    batch_id = fields.Many2one('lims.batch')
    state = fields.Selection(get_state)
    assigned_to = fields.Many2one('res.users', 'Assigned to')
    date = fields.Datetime('Date')
