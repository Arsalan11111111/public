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
from odoo import fields, models, api, exceptions


class SpwTaxVisitCpt(models.Model):
    _inherit = 'spw.tax.visit.cpt'

    def spw_tax_report_xlsx_template(self):
        res = {
            'ID odoo': self.id or '',
            'ID pt de prélèvement': self.sampling_point_id.name or '',
            'Date de': self.date_from or '',
            'Date de fin': self.date_to or '',
            'planifié': self.planned or '',
            'compté': self.counted or '',
        }
        return res

    def rec_analysis_id(self, data):
        analysis_name = ''
        for campaign_id in data.get('campaign_ids'):
            tax_campaign_id = self.env['spw.tax.campaign'].browse(campaign_id)
            for analysis_id in tax_campaign_id.analysis_ids:
                if analysis_id.extraction_point_id.id == self.extraction_point_id.id:
                    analysis_name += analysis_id.name + ' '
            if analysis_name:
                analysis_name = analysis_name[:-1]
        return analysis_name
