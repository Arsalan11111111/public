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


class AssignCampaignWizard(models.TransientModel):
    _name = 'assign.campaign.wizard'
    _description = "Assign Campaign Wizard"

    def get_site_id(self):
        if self.env.context.get('active_ids'):
            analysis_id = self.env['lims.analysis'].browse(self.env.context.get('active_ids')[0])
            return analysis_id.partner_address_id.id

    def get_partner_id(self):
        if self.env.context.get('active_ids'):
            analysis_id = self.env['lims.analysis'].browse(self.env.context.get('active_ids')[0])
            return analysis_id.partner_id.id

    campaign_id = fields.Many2one('spw.tax.campaign', 'Campaign', domain=lambda self: self._get_campaign_domain())
    date_sample = fields.Date('Date Sample')
    date_sample_receipt = fields.Date('Date Sample Receipt')
    date_plan = fields.Date('Date Plan')
    site_id = fields.Many2one('res.partner', default=get_site_id)
    partner_id = fields.Many2one('res.partner', default=get_partner_id)

    @api.model
    def _get_campaign_domain(self):
        if self.env.context.get('active_model') == 'lims.analysis' and self.env.context.get('active_id'):
            analysis_ids = self.env['lims.analysis'].search([('id', 'in', self.env.context.get('active_ids'))])
            site_id = analysis_ids[0].partner_address_id.id
            if site_id:
                if len(analysis_ids.search([
                    ('partner_address_id', '=', site_id),
                    ('id', 'in', analysis_ids.ids)
                ])) < len(analysis_ids):
                    raise exceptions.ValidationError(
                        _('You can only assign analysis with the same site to the same campaign'))
            else:
                raise exceptions.ValidationError(_("You can't assign a campaign to analysis without extraction site"))
            return [('site_id', '=', site_id), ('state', '=', 'open')]
        return []

    @api.onchange('campaign_id')
    def onchange_campaign_id(self):
        self.date_sample = self.campaign_id.date
        self.date_sample_receipt = self.campaign_id.date_end

    def confirm_assign_campaign(self):
        analysis_ids = self.env['lims.analysis'].search([('id', 'in', self.env.context.get('active_ids'))])
        for analysis_id in analysis_ids:
            analysis_id.write({
                'campaign_id': self.campaign_id.id,
                'date_sample': self.date_sample,
                'date_plan': self.date_plan,
                'date_sample_receipt': self.date_sample_receipt,
                'taxe': True,
            })
