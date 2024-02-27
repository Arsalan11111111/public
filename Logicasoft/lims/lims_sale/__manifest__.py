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
    'name': 'LIMS Sale',
    'version': '16.0.1.20',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add actions to generate sale orders from Lims analysis requests and Lims analysis.',
    'sequence': 97,
    'description': """
    LIMS Sale : Generate SO from analysis and analysis request.
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_base', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_actions_server.xml',

        'views/res_config.xml',
        'views/lims_analysis.xml',
        'views/lims_analysis_request.xml',
        'views/lims_method_parameter_characteristic.xml',
        'views/sale_order_view.xml',
        'views/product_template.xml',
        'views/lims_laboratory.xml',
        'views/lims_parameter_pack.xml',
        'views/lims_analysis_request_sample.xml',
        'views/lims_request_product_pack.xml',

        'views/lims_portal_request.xml',
        'views/lims_portal_analysis.xml',
        'views/sale_portal_templates.xml',

        'reports/lims_analysis_request_report.xml',
        'reports/sale_report_templates.xml',

        'wizards/confirm_create_order_wizard.xml',
        'wizards/confirm_create_order_request_wizard.xml',
        'wizards/create_analysis_request_wizard.xml',
    ],
    'demo': [
        'demo/lims_demo_product.xml',
        'demo/lims_demo_method_parameter_characteristic.xml',
        'demo/lims_demo_parameter_pack.xml',
        'demo/lims_demo_data_analysis_request.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'lims_sale/static/src/*/*.xml',
        ]
    },
    'css': [],
    'test': [],
    'installable': True,
    'post_init_hook': '_lims_sale_request_invoice_id_post_init',
}
