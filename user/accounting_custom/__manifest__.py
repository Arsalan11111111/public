# -*- coding: utf-8 -*-

{
    'name': 'accounting custom ',
    'author': "Azam Mustafa",
    'category': 'Payroll',
    'version': '16.0.0.0',
    'license': 'LGPL-3',
    'summary': '',
    'description': """ """,
    'depends': ['base','account','account_reports','hr','purchase'],
    'data': [
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/report_templates.xml',
        'data/account_partner_balance.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'accounting_custom/static/src/js/report_currency_minimize.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
