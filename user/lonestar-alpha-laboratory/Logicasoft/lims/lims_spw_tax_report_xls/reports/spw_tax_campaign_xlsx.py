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
from odoo import models


class SpwTaxCampaignXlsx(models.AbstractModel):
    _name = 'report.lims_spw_tax_report_xls.report_tax_xlsx'
    _description = 'Report Lims_spw_tax_report_xls Report_tax_xlsx model'
    _inherit = 'report.report_xlsx.abstract'

    nb_row = fields.Integer(default=1)

    def generate_xlsx_report(self, workbook, data, campaign_ids):
        self.nb_row = 1
        sheet_campaign = workbook.add_worksheet('campaign')

        self.add_header_sheet(self.env['spw.tax.campaign'].spw_tax_report_xlsx_template(), sheet_campaign, workbook)
        for campaign_id in campaign_ids:
            self.add_data_sheet(campaign_id.spw_tax_report_xlsx_template(), sheet_campaign, workbook)

        sheet_meters = workbook.add_worksheet('Compteurs')
        self.nb_row = 1
        self.add_header_sheet(self.env['spw.tax.meter.reading'].spw_tax_report_xlsx_template(), sheet_meters, workbook)
        for campaign_id in campaign_ids:
            for meters_reading_id in campaign_id.meters_reading_ids:
                self.add_data_sheet(meters_reading_id.spw_tax_report_xlsx_template(), sheet_meters, workbook)

        sheet_client = workbook.add_worksheet('client')
        self.nb_row = 1
        self.add_header_sheet(self.env['res.partner'].spw_tax_report_xlsx_template(), sheet_client, workbook)
        for campaign_id in campaign_ids:
            self.add_data_sheet(campaign_id.site_id.spw_tax_report_xlsx_template(), sheet_client, workbook)

        sheet_contact = workbook.add_worksheet('client (tax contact)')
        self.nb_row = 1
        self.add_header_sheet(self.env['res.partner'].spw_tax_report_xlsx_template(), sheet_contact, workbook)
        for campaign_id in campaign_ids:
            for contact_id in campaign_id.partner_id.child_ids:
                if contact_id.tax_contact:
                    self.add_data_sheet(contact_id.spw_tax_report_xlsx_template(), sheet_contact, workbook)

        sheet_cpt_tax = workbook.add_worksheet('compteur tax')
        self.nb_row = 1
        self.add_header_sheet(self.env['spw.tax.visit.cpt'].spw_tax_report_xlsx_template(), sheet_cpt_tax, workbook)
        for campaign_id in campaign_ids:
            for sampling_point_id in campaign_id.sampling_point_ids:
                for cpt_tax_id in sampling_point_id.cpt_tax_ids:
                    self.add_data_sheet(cpt_tax_id.spw_tax_report_xlsx_template(), sheet_cpt_tax, workbook)

        sheet_meters_reading = workbook.add_worksheet('Relevé compteurs')
        self.nb_row = 1
        self.add_header_sheet(
            self.env['spw.tax.meter.reading'].spw_tax_report_xlsx_template(), sheet_meters_reading, workbook
        )
        for campaign_id in campaign_ids:
            for meters_reading_id in campaign_id.meters_reading_ids:
                self.add_data_sheet(meters_reading_id.spw_tax_report_xlsx_template(), sheet_meters_reading, workbook)

        sheet_analysis = workbook.add_worksheet('Analysis')
        self.nb_row = 1
        self.add_header_sheet(self.env['lims.analysis'].spw_tax_report_xlsx_template(), sheet_analysis,
                              workbook)

        for campaign_id in campaign_ids:
            for analysis_id in campaign_id.analysis_ids:
                self.add_data_sheet(analysis_id.spw_tax_report_xlsx_template(), sheet_analysis, workbook)

        sheet_analysis_result = workbook.add_worksheet('Analysis results')
        self.nb_row = 1
        self.add_header_sheet(self.env['lims.analysis.result'].spw_tax_report_xlsx_template(), sheet_analysis_result,
                              workbook)
        for campaign_id in campaign_ids:
            for analysis_id in campaign_id.analysis_ids:
                for analysis_result_id in analysis_id.result_num_ids:
                    if analysis_result_id.state in ['conform']:
                        self.add_data_sheet(
                            analysis_result_id.spw_tax_report_xlsx_template(),
                            sheet_analysis_result,
                            workbook
                        )

        analysis_result_taxes = workbook.add_worksheet('Analysis results taxes')
        self.nb_row = 1
        self.add_header_sheet(self.env['lims.analysis.result'].spw_tax_report_xlsx_template(), analysis_result_taxes,
                              workbook)
        for campaign_id in campaign_ids:
            for analysis_id in campaign_id.analysis_ids:
                for analysis_result_id in analysis_id.result_num_ids:
                    if analysis_result_id.state in ['done']:
                        if analysis_result_id.parameter_id.is_taxes:
                            self.add_data_sheet(
                                analysis_result_id.spw_tax_report_xlsx_template(),
                                analysis_result_taxes,
                                workbook
                            )

        sheet_sampling_point = workbook.add_worksheet('Point prel')
        self.nb_row = 1
        self.add_header_sheet(self.env['lims.sampling.point'].spw_tax_report_xlsx_template(), sheet_sampling_point,
                              workbook)
        for campaign_id in campaign_ids:
            for sampling_point_id in campaign_id.sampling_point_ids:
                self.add_data_sheet(sampling_point_id.spw_tax_report_xlsx_template(), sheet_sampling_point, workbook)

        sheet_changes_campaign_treated_mat = workbook.add_worksheet('Matières traitées')
        self.nb_row = 1
        self.add_header_sheet(
            self.env['spw.tax.campaign.treatedmat'].spw_tax_report_xlsx_template(),
            sheet_changes_campaign_treated_mat,
            workbook)
        for campaign_id in campaign_ids:
            for treated_mat_id in campaign_id.treated_mat_ids:
                self.add_data_sheet(
                    treated_mat_id.spw_tax_report_xlsx_template(),
                    sheet_changes_campaign_treated_mat,
                    workbook)

        sheet_activity = workbook.add_worksheet('Activité client')
        self.nb_row = 1
        self.add_header_sheet(self.env['spw.tax.partner.activity'].spw_tax_report_xlsx_template(), sheet_activity,
                              workbook)
        for campaign_id in campaign_ids:
            for activity_spw_tax_id in campaign_id.site_id.activity_spw_tax_ids:
                self.add_data_sheet(activity_spw_tax_id.spw_tax_report_xlsx_template(), sheet_activity, workbook)

    def add_data_sheet(self, data, sheet, workbook):
        nb_col = 0
        bold = workbook.add_format({'bold': True})
        for key, val in data.items():
            sheet.write(self.nb_row, nb_col, val)
            nb_col += 1

        self.nb_row += 1

    def add_header_sheet(self, data, sheet, workbook):
        nb_col = 0
        bold = workbook.add_format({'bold': True})
        for key, val in data.items():
            sheet.write(self.nb_row - 1, nb_col, key, bold)
            nb_col += 1
