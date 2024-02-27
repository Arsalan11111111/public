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
from datetime import date


class LimsSamplingPoint(models.Model):
    _inherit = 'lims.sampling.point'

    tax = fields.Boolean('Tax')
    rain_water_presence = fields.Boolean('Rain Water Presence')
    comment = fields.Text('Comment')

    discharge_water_type_id = fields.Many2one('spw.tax.discharge.water.type', 'Discharge Water Type')
    discharge_type_id = fields.Many2one('spw.tax.discharge.type', 'Discharge Type')
    treatment_id = fields.Many2one('spw.tax.treatment', 'Treatment')
    control_point_id = fields.Many2one('spw.tax.control.point', 'Control Point')
    flowmeter_id = fields.Many2one('maintenance.equipment', 'Flowmeter')
    sampler_id = fields.Many2one('maintenance.equipment', 'Sampler')
    discharge_media_id = fields.Many2one('spw.tax.discharge.media', 'Discharge Media')

    cpt_tax_ids = fields.One2many('spw.tax.visit.cpt', 'sampling_point_id', 'Tax Frequency')
    campaign_ids = fields.Many2many('spw.tax.campaign', string='Campaigns')
    nb_campaigns = fields.Integer('Number Campaigns', compute='compute_nb_campaigns')

    reference = fields.Char('Reference')
    frequency = fields.Integer('Frequency')

    is_sampling_punctual = fields.Boolean('Punctual', default=False)
    is_sampling_time_composite = fields.Boolean('Time Composite', default=False)
    is_sampling_composite_flow = fields.Boolean('Composite Flow', default=False)

    sampling_spill_number = fields.Char('Spill N°')
    is_sampling_under_seal = fields.Boolean('Under seal')
    is_sampling_continuous_debit = fields.Boolean('Continuous flow')
    is_sampling_statement_spill_counter = fields.Boolean('statement spill counter')
    is_sampling_debit_other_estimate = fields.Boolean('debit other estimate')
    sampling_other_debit_measure = fields.Char('other debit measurement')
    sampling_other_methodology_description = fields.Many2one('spw.tax.other.methodology.description',
                                                             string='other methodology description')
    is_sampling_under_seal_debit = fields.Boolean('Under seal debit')
    is_sampling_equipment_labo = fields.Boolean('Labo', help="Sampling equipment used is from laboratory")
    is_sampling_equipment_site = fields.Boolean('Site', help="Sampling equipment used if from site")
    is_equipment_labo = fields.Boolean('Labo', help="Equipment used to measure debit is from laboratory")
    is_equipment_site = fields.Boolean('Site', help="Equipment used to measure debit is from site")

    @api.depends('campaign_ids')
    def compute_nb_campaigns(self):
        for record in self:
            record.nb_campaigns = len(record.campaign_ids)

    @api.model
    def create(self, vals):
        res = super(LimsSamplingPoint, self).create(vals)
        res.create_visit_cpt()
        return res

    def write(self, vals):
        for record in self:
            res = super(LimsSamplingPoint, record).write(vals)
            if record.tax and not record.cpt_tax_ids:
                record.create_visit_cpt()
        return res

    def create_visit_cpt(self):
        for record in self:
            if record.tax:
                years = self.env['ir.config_parameter'].sudo().get_param('years_create_tax')
                if years:
                    years = years.split(';')
                    for year in years:
                        self.env['spw.tax.visit.cpt'].create({
                            'sequence': int(year),
                            'date_from': date(int(year), 1, 1),
                            'date_to': date(int(year), 12, 31),
                            'planned': record.frequency or 0,
                            'sampling_point_id': record.id,
                        })

    def button_list_campaign(self):
        action = {
                'type': 'ir.actions.act_window',
                'res_model': 'spw.tax.campaign',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.campaign_ids.ids)]
                }
        return action
