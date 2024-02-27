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


class RequestMassChangeWizard(models.TransientModel):
    _name = 'request.mass.change.wizard'
    _description = 'Request Mass Change'

    line_ids = fields.One2many('request.mass.change.wizard.line', 'wizard_id')
    state = fields.Selection([('accepted', _('Accepted')), ('cancel', _('Cancelled'))])

    @api.model
    def default_get(self, fields_list):
        res = super(RequestMassChangeWizard, self).default_get(fields_list)
        request_ids = self.env['lims.analysis.request'].browse(self.env.context.get('active_ids'))
        res.update({
            'line_ids': [(0, 0, {
                'request_id': request_id.id,
            }) for request_id in request_ids.filtered(lambda r: r.state in ['draft', 'accepted', 'in_progress'])],
        })
        return res

    def save_mass_change(self):
        if self.state == 'accepted':
            self.line_ids.mapped('request_id').do_confirmed()
        elif self.state == 'cancel':
            self.line_ids.mapped('request_id').do_cancel()


class RequestMassChangeWizardLine(models.TransientModel):
    _name = 'request.mass.change.wizard.line'
    _description = 'Request Mass Change Line'

    wizard_id = fields.Many2one('request.mass.change.wizard')
    request_id = fields.Many2one('lims.analysis.request')

