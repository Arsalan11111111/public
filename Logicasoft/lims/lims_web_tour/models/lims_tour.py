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
from odoo import models, fields, api


class LimsTour(models.Model):
    _inherit = 'lims.tour'

    @api.model
    def create(self, vals):
        res = super(LimsTour, self).create(vals)
        if vals.get('sampler_team_id'):
            res.add_team_followers(vals.get('sampler_team_id'))
        return res

    def write(self, vals):
        if vals.get('sampler_team_id'):
            self.add_team_followers(vals.get('sampler_team_id'))
        res = super(LimsTour, self).write(vals)
        return res

    def add_team_followers(self, sampler_team_id):
        new_sampler_team_id = self.env['lims.sampler.team'].browse(sampler_team_id)
        for record in self.filtered(lambda r: r.sampler_team_id):
            record.message_unsubscribe(partner_ids=record.sampler_team_id.mapped('sampler_ids.user_id').ids)
            record.tour_line_ids.mapped('analysis_id').message_unsubscribe(
                partner_ids=record.sampler_team_id.mapped('sampler_ids.user_id').ids)
        for record in self:
            record.message_subscribe(partner_ids=new_sampler_team_id.mapped('sampler_ids.user_id').ids)
            record.tour_line_ids.mapped('analysis_id').message_subscribe(
                partner_ids=new_sampler_team_id.mapped('sampler_ids.user_id').ids)
