# -*- coding: utf-8 -*-
{
    'name': "atawah_amount_discount",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'product', 'purchase','account_followup','account_custom_analytic','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/res_company.xml',
        'wizard/account_change_lock_date.xml',
        'wizard/check_lock_pass.xml',
        'wizard/save_ex_report_wizard_view.xml',
        'reports/partner_details.xml',
        'reports/partner_details_action.xml',
        'views/purchase_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
