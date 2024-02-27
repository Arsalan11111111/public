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


class SpwTaxPartnerActivity(models.Model):
    _inherit = 'spw.tax.partner.activity'

    def spw_tax_report_xlsx_template(self):
        res = {
            'ID odoo': self.id or '',
            'Secteur d activité': self.name or '',
            'Code secteur': self.code or '',
            'Ecotoxicité': self.ecotoxicity or '',
            'Jours d activité (comptage)': self.days_activity_count or '',
            'Jours de rejet': self.days_discharge_count or '',
            'Mois d activité': self.month_activity_id.name,
            'Jours d activité': self.get_name_day_activity_ids() or '',
            'Mois d activité': self.get_name_month_activity_ids() or '',
        }
        return res

    def get_name_day_activity_ids(self):
        name = ''
        for day_activity_id in self.day_activity_ids:
            name += day_activity_id.name + ','
        return name

    def get_name_month_activity_ids(self):
        name = ''
        for month_activity_id in self.month_activity_ids:
            name += month_activity_id.name + ','
        return name
