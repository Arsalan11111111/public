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
    'name': 'LIMS Scan Advanced',
    'version': '16.0.1.1',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add scan actions to assign tests and a new entry in main menu.',
    'sequence': 98,
    'description': """
    Lims scan advanced : Creates a specific entry for scanning.
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_scan', 'stock_barcode'],
    'data': [
        'data/ir_actions_server.xml',

        'reports/barcode_action.xml',
        'reports/barcode_user.xml',
        'reports/qrcode_action.xml',

        'wizards/sop_scan_receipt_wizard.xml',
        'wizards/sop_scan_wip_wizard.xml',
        'wizards/sop_scan_batch_wizard.xml',

        'views/lims_sop.xml',
        'views/menu.xml',
    ],
    'css': [],
    'qweb': [
        "static/src/xml/lims_barcode.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'lims_scan_advanced/static/src/js/*.js',
            'lims_scan_advanced/static/src/xml/*.xml',
        ],
    },
    'test': [],
    'installable': True,
}
