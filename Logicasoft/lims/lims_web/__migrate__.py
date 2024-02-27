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
    'name': 'LIMS Web',
    'version': '15.0.0.7',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'description': """
    LIMS Web : Add analysis and analysis request on portal. (Customer must be follower.) 
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['portal', 'website', 'lims_report'],
    'data': [
        'security/ir.model.access.csv',

        'views/lims_analysis_portal.xml',
        'views/lims_portal_template.xml',
        'views/lims_request_portal.xml',
        'views/lims_website_template.xml',
        'views/lims_method.xml',
        'views/lims_method_parameter_characteristic.xml',
        'views/res_config_settings.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/lims_web/static/src/js/portal.js',
            '/lims_web/static/src/lib/xlsx-0.17.0.min.js',
            '/lims_web/static/src/js/export.js',
            '/lims_web/static/src/js/lims_web.js',
        ]
    },
    'css': [],
    'test': [],
    'installable': True,
}
