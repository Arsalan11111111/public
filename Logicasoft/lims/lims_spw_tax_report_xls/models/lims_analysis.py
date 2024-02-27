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


class LimsAnalysis(models.Model):
    _inherit = "lims.analysis"

    def spw_tax_report_xlsx_template(self):
        res = {
            'ID odoo': self.id or '',
            'ID analyse': self.name or '',
            'Nom ech': self.sample_name or '',
            'Demande': self.request_id.name or '',
            'Client': self.partner_id.name or '',
            'Site prélèvement': self.partner_address_id.name or '',
            'Point prélèvement': self.sampling_point_id.name or '',
            'ID Campagne': self.campaign_id.name or '',
            'Matrice': self.matrix_id.name or '',
            'Type echantillonnage': self.matrix_id.name or '',
            'Catégorie': self.category_id.name or '',
            'Statut': self.state or '',
            'Date ech. Début': self.date_sample_begin or '',
            'Date ech. Fin': self.date_sample or '',
            'Date réception ech.': self.date_sample_receipt or '',
            'Préleveur': self.sampler_id.name or '',
            'Date debut analyse': self.date_start or '',
            'Date fin analyse': self.date_done or '',
            'Référence': self.customer_ref or '',
            'Point de contrôle': self.control_point_id.name or '',
            'Echantillonneur': self.sampling_equipment_id.name or '',
            'Ech. Par client': self.external_sampling or '',
            'Débitmètre': self.flowmeter_id.name or '',
            'Débitmètre client': self.flowmeter_is_customer or '',
            'Débit par CEB': self.flowmeter_is_check_by_us or '',
            'Pas de débitmètre': self.read_by_none or '',
            'Débit lu par cient': self.read_by_customer or '',
            'Ponctuel': self.is_punctual or '',
            'Composite temps': self.is_time_composite or '',
            'Composite débit': self.is_composite_flow or '',
            'Transport réfrigéré': self.is_refrigerated_transport or '',
            'Commentaire': self.sampling_comment or '',
            'Volume prélevé': self.sampling_volume or '',
            'contre échantillon': self.counter_sampler or '',

        }
        return res
