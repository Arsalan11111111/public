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
{
    'name': 'LIMS SPW Tax',
    'version': '16.0.0.1',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'description': """
    LIMS SPW Tax : Module for Wallonia (BE) SPW tax
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_sampling', 'lims_maintenance'],
    'data': [
        'data/ir_sequence.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/spw_tax_campaign_view.xml',
        'views/res_partner_view.xml',
        'views/lims_sampling_point_view.xml',
        'views/spw_tax_accessibility_view.xml',
        'views/spw_tax_campaign_produced_view.xml',
        'views/spw_tax_campaign_treatedmat_view.xml',
        'views/spw_tax_control_point_view.xml',
        'views/spw_tax_day_view.xml',
        'views/spw_tax_discharge_media_view.xml',
        'views/spw_tax_discharge_type_view.xml',
        'views/spw_tax_discharge_water_type_view.xml',
        'views/spw_tax_meter_view.xml',
        'views/spw_tax_meter_reading_view.xml',
        'views/spw_tax_month_view.xml',
        'views/spw_tax_partner_activity_view.xml',
        'views/spw_tax_treatment_view.xml',
        'views/spw_tax_visit_cpt_view.xml',
        'views/spw_tax_watertype_view.xml',
        'views/product_template_view.xml',
        'views/lims_analysis_view.xml',
        'views/lims_config_settings.xml',

        'wizards/assign_campaign_wizard_view.xml',
    ],
    'css': [],
    'test': [],
    'installable': True,
}
