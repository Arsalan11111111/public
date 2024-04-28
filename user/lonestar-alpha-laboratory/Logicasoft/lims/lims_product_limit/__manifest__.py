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
    'name': 'LIMS Product Limit',
    'version': '16.0.1.8',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add product-related parameter limits instead of limits defined directly in the parameters.',
    'sequence': 98,
    'description': """
     Use the limit defined by the product instead of the standard
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_report'],
    'data': [
        'data/ir_actions_server.xml',

        'security/ir.model.access.csv',

        'views/lims_method_parameter_characteristic.xml',
        'views/lims_method_parameter_characteristic_limit_product.xml',
        'views/lims_parameter_char_product.xml',

        'wizards/mass_duplicate_product_limit_wizard.xml',
        'wizards/generate_limit_product_variant_wizard.xml',
    ],
    'demo': [
        'demo/lims_demo_product.xml',
        'demo/lims_demo_parameter_char_product.xml',
        'demo/lims_demo_parameter_char_limit_product.xml',
    ],
    'css': [],
    'test': [],
    'installable': True,
}
