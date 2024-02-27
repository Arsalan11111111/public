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


class SpwTaxCampaign(models.Model):
    _name = 'spw.tax.campaign'
    _description = 'Spw Tax Campaign model'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True, translate=True)
    type = fields.Selection('get_type', 'Type')
    parent_id = fields.Many2one('spw.tax.campaign', 'Parent')
    date = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    site_id = fields.Many2one('res.partner', 'Site',
                              domain="[('is_sampling_point', '=', True), ('parent_id', '=', partner_id)]")

    sampling_point_ids = fields.Many2many('lims.sampling.point', string='Samplin point')
    meters_reading_ids = fields.One2many('spw.tax.meter.reading', 'campaign_id', string='Meters Reading')
    treated_mat_ids = fields.One2many('spw.tax.campaign.treatedmat', 'campaign_id', 'Treated Mat')
    produced_mat_ids = fields.One2many('spw.tax.campaign.produced', 'campaign_id', 'Produced Mat')
    analysis_ids = fields.One2many('lims.analysis', 'campaign_id', 'Analysis')

    nb_employees = fields.Float('Employees', related='site_id.nb_employees', readonly=True)
    nb_workers = fields.Float('Workers', related='site_id.nb_workers', readonly=True)
    no_com = fields.Boolean('No communicated', related='partner_id.no_com', readonly=True)

    nb_analysis = fields.Integer('Nb Analysis', compute='compute_nb_analysis')

    state = fields.Selection([('open', 'Open'), ('done', 'Done')], 'State', default='open')
    export = fields.Boolean('Export')

    @api.onchange('site_id')
    def onchange_site_id(self):
        sampling_point_obj = self.env['lims.sampling.point']
        sampling_point_ids = sampling_point_obj.search([('partner_id', '=', self.site_id.id),
                                                            ('tax', '=', True)])
        self.sampling_point_ids = sampling_point_ids
        meter_ids = self.site_id.meter_ids
        meter_reading_obj = self.env['spw.tax.meter.reading']
        existing_meter_ids = [meter_reading.meter_id.id for meter_reading in self.meters_reading_ids]
        for meter_id in meter_ids:
            if meter_id.id not in existing_meter_ids:
                self.meters_reading_ids += meter_reading_obj.create({'meter_id': meter_id.id})

    @api.model
    def get_type(self):
        return [('view', 'View'),
                ('campaign', 'Campaign')]

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.analysis_ids)

    def button_list_analysis(self):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.analysis_ids.ids)],
            'context': {'no_create': True},
        }
        return action
