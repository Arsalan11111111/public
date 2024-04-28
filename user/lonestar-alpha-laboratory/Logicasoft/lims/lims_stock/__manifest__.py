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
    'name': 'LIMS Stock',
    'version': '16.0.0.1',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add a new action on stock moves: the creation of analysis from this move + a link between an analysis and a product lot.',
    'sequence': 98,
    'description': """
    Lims stock : add analysis on product move in Inventory app + link an analysis to a product lot
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_base', 'stock'],
    'data': [
        'security/ir.model.access.csv',

        'data/ir_actions_server.xml',

        'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/stock_move_line.xml',
        'views/lims_analysis.xml',
        'views/lims_analysis_request.xml',
        'views/lims_sop.xml',
        'views/stock_lot.xml',

        'wizards/stock_move_lot_wizard.xml',
        'wizards/create_analysis_wizard.xml',
        'wizards/lims_history.xml',

        'reports/lims_analysis_worksheet.xml',
    ],
    'demo': [
        'demo/lims_demo_product_inventory.xml',
        'demo/lims_demo_picking_type.xml',
        'demo/lims_demo_stock_picking.xml',
    ],
    'css': [],
    'test': [],
    'installable': True,
}
