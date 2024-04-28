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
    'name': 'LIMS conditional tests',
    'version': '16.0.0.8',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add additional tests when the value of a result reaches a specific value.',
    'sequence': 98,
    'description': """
    Lims conditional tests : Adds additional tests when the value of a result reaches a specific value 
    (configured in the limits of the Lims)
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_partner_limit', 'lims_product_limit'],
    'data': [
        'views/lims_method_parameter_characteristic.xml',
        'views/lims_result_value.xml',
        'views/lims_parameter_char_product.xml',
        'views/lims_parameter_char_partner.xml',
        'views/lims_analysis_limit_result.xml',
        'views/lims_analysis_compute_result.xml',
        'views/lims_method_parameter_characteristic_limit.xml',
    ],
    'demo': [
        'demo/lims_demo_method_parameter_characteristic.xml',
        'demo/lims_demo_result_value.xml',
    ],
    'css': [],
    'test': [],
    'installable': True,
}
