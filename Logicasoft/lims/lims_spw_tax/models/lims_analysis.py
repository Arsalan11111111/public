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
from lxml import etree


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    campaign_id = fields.Many2one('spw.tax.campaign', 'Campaign')
    control_point_id = fields.Many2one('spw.tax.control.point', 'Control Point')
    sampling_volume = fields.Float('Sampling Volume (l)')
    taxe = fields.Boolean('Taxe', default=False)
    flowmeter_id = fields.Many2one('maintenance.equipment', 'Flowmeter')
    sampling_equipment_id = fields.Many2one('maintenance.equipment', 'Sampling equipment')
    partner_address_id = fields.Many2one('res.partner', 'Extraction Site')

    sampler_asset_id = fields.Many2one('maintenance.equipment', 'Labo (N° INV)')
    sampler_is_customer = fields.Boolean('Customer equipment', default=False)
    sampler_is_check_by_us = fields.Boolean('Check by Us', default=False)
    is_punctual = fields.Boolean('Punctual', default=False)
    is_time_composite = fields.Boolean('Time Composite', default=False)
    is_composite_flow = fields.Boolean('Composite Flow', default=False)
    is_planning = fields.Boolean('Planning', default=False)
    is_date_unknown = fields.Boolean('Date Unknown', default=False)
    is_done_by_client = fields.Boolean('Done by Client', default=False)
    flowmeter_asset_id = fields.Many2one('maintenance.equipment', 'Labo (N° INV) ')
    flowmeter_is_customer = fields.Boolean('Customer sampler', default=False)
    flowmeter_is_check_by_us = fields.Boolean('Check by Us ', default=False)
    is_refrigerated_transport = fields.Boolean('Refrigerated Transport')
    sampling_comment = fields.Char('Sampling Comment')

    is_supervision = fields.Boolean("Supervision")
    is_statement = fields.Boolean("Statement")
    is_statement_A1 = fields.Boolean("Statement A1")
    is_statement_A2 = fields.Boolean("Statement A2")
    is_statement_B = fields.Boolean("Statement B")
    is_under_seal = fields.Boolean('Under seal')

    is_sample_equipment_labo = fields.Boolean('Sample Labo')
    is_sample_equipment_site = fields.Boolean('Sample Site')

    is_continuous_debit = fields.Boolean('Continuous flow')
    continuous_debit_measure = fields.Char('Continuous debit measurement')
    is_statement_spill_counter = fields.Boolean('statement spill counter')

    statement_date_start = fields.Datetime('statement start date')
    statement_date_end = fields.Datetime('statement end date')
    statement_index_start = fields.Float('statement start index', digits=(12, 5))
    statement_index_end = fields.Float('statement end index', digits=(12, 5))

    is_debit_other_estimate = fields.Boolean('debit other estimate')
    other_debit_measure = fields.Char('other debit measurement')
    other_methodology_description = fields.Many2one('spw.tax.other.methodology.description')

    is_equipment_labo = fields.Boolean('Labo')
    is_equipment_site = fields.Boolean('Site')
    is_under_seal_debit = fields.Boolean('Under seal debit')

    is_note1 = fields.Boolean('Obstruct by taxpayer')
    is_note2 = fields.Boolean('Sampling difficulty')
    is_note3 = fields.Boolean('Flow measurement difficulty')
    is_note4 = fields.Boolean('Other')
    note_txt = fields.Text(string='Note printed on spw tax')

    #  Sampling Information
    read_by_labo = fields.Boolean('Read By Labo')
    read_by_none = fields.Boolean('None')
    read_by_customer = fields.Boolean('Read By Customer')

    @api.model
    def create(self, vals):
        if vals.get('sampling_point_id'):
            sampling_point_id = self.env['lims.sampling.point'].browse(vals['sampling_point_id'])
            vals.update(self.get_sampling_point_vals(sampling_point_id))
        return super(LimsAnalysis, self).create(vals)

    def write(self, vals):
        if vals.get('sampling_point_id'):
            sampling_point_id = self.env['lims.sampling.point'].browse(vals['sampling_point_id'])
            vals.update(self.get_sampling_point_vals(sampling_point_id))
        return super(LimsAnalysis, self).write(vals)

    def get_sampling_point_vals(self, sampling_point_id):
        sampling_point_vals = {
            'flowmeter_id': sampling_point_id.flowmeter_id.id,
            'sampler_asset_id': sampling_point_id.sampler_id.id,
            'is_under_seal': sampling_point_id.is_sampling_under_seal,
            'is_continuous_debit': sampling_point_id.is_sampling_continuous_debit,
            'is_statement_spill_counter': sampling_point_id.is_sampling_statement_spill_counter,
            'is_debit_other_estimate': sampling_point_id.is_sampling_debit_other_estimate,
            'other_methodology_description': sampling_point_id.sampling_other_methodology_description.id,
            'is_punctual': sampling_point_id.is_sampling_punctual,
            'is_time_composite': sampling_point_id.is_sampling_time_composite,
            'is_composite_flow': sampling_point_id.is_sampling_composite_flow,
            'is_sample_equipment_labo': sampling_point_id.is_sampling_equipment_labo,
            'is_sample_equipment_site': sampling_point_id.is_sampling_equipment_site,
            'is_equipment_labo': sampling_point_id.is_equipment_labo,
            'is_equipment_site': sampling_point_id.is_equipment_site,
            'is_under_seal_debit': sampling_point_id.is_sampling_under_seal_debit,
        }
        return sampling_point_vals

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        Hide the possibility to create, edit or delete analysis accessed via button 'analysis' of spw.tax.campaign
        '''
        res = super(LimsAnalysis, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                       submenu=submenu)
        if self.env.context.get('no_create'):
            doc = etree.XML(res['arch'])
            for t in doc.xpath("//tree"):
                t.attrib['create'] = 'false'
                t.attrib['delete'] = 'false'
            for t in doc.xpath("//form"):
                t.attrib['create'] = 'false'
                t.attrib['delete'] = 'false'
            res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('date_sample')
    def on_change_date_sample(self):
        for record in self:
            record.date_sample_begin = record.date_sample
