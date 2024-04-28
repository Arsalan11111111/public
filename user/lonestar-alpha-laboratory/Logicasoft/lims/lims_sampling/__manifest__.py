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
    'name': 'LIMS Sampling Point',
    'version': '16.0.1.6',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add sampling point managment in Lims analysis.',
    'sequence': 98,
    'description': """
    LIMS Sampling Point : add sampling point management in the LIMS.
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_base'],
    'data': [
        'security/ir.model.access.csv',

        'views/menu_item.xml',
        'views/lims_sampling_category.xml',
        'views/lims_sampling_point_location.xml',
        'views/lims_sampling_point.xml',
        'views/lims_quality_zone.xml',
        'views/lims_analysis.xml',
        'views/lims_analysis_compute_result.xml',
        'views/lims_analysis_numeric_result.xml',
        'views/lims_analysis_sel_result.xml',
        'views/lims_sop.xml',
        'views/lims_sampling_type.xml',
        'views/lims_sampling_tag.xml',
        'views/lims_analysis_text_result.xml',
        'views/lims_analysis_request.xml',
        'views/res_partner.xml',

        'views/lims_portal_analysis.xml',

        'wizards/create_analysis_wizard_sampling.xml',
        'wizards/create_analysis_wizard.xml',
        'wizards/analysis_mass_change_wizard.xml',
        'wizards/lims_history.xml',

        'reports/container_report.xml',
    ],
    'demo': [
        'demo/lims_demo_hr_employee.xml',
        'demo/lims_demo_quality_zone.xml',
        'demo/lims_demo_sampling_category.xml',
        'demo/lims_demo_sampling_point_location.xml',
        'demo/lims_demo_sampling_tag.xml',
        'demo/lims_demo_sampling_type.xml',
        'demo/lims_demo_sampling_point.xml',
        'demo/lims_demo_analysis.xml',
        'demo/lims_demo_analysis_request_sample.xml',
    ],
    'assets': {
        'web.assets_tests': [
            'lims_sampling/static/tests/**/*',
        ],
    },
    'css': [],
    'test': [],
    'installable': True,
}
