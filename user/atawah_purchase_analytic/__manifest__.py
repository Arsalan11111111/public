# -*- coding: utf-8 -*-
{
    'name': "Atawah Purchase Analytic",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com..",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'account',
        'account_accountant',
        'partner_name_hide_parent'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/purchase_order.xml',
        'views/account_bank_statement_line.xml',
        'views/account_payment.xml',
        'views/account_move.xml',
        'views/res_partner.xml',
        'reports/invoice_report.xml',
        'reports/account_bank_statement_line_report.xml',
        'reports/account_bank_statement_line_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/atawah_purchase_analytic/static/src/css/header.css',
            '/atawah_purchase_analytic/static/src/js/one2manySearch.js',
            '/atawah_purchase_analytic/static/src/xml/one2manysearch.xml',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'sequence': -1,
    'application': True
}
