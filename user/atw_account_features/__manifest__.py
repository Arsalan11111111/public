# -*- coding: utf-8 -*-

{
    'name': 'Account Features',
    'version': '16.0.0.5',
    'category': 'Account',
    'sequence': -1,
    'application': True,
    'license': 'OPL-1',
    'summary': 'Features related to account specific.',
    'description': """
        0.0.1 : Get due date even after selecting payment terms.
        0.0.2 : Get anaytic accounts from product profile in account move line.
        0.0.3 : Add domain to only select related shipping address of the selected
                partner in invoice.
        0.0.4 : Take the fields primary and secondary delivery ids of module "atawah_purchase_analytic"
                and use them in the account move and moveline search view.
        0.0.5 : Add LPO in invoice search view.

    """,
    'author': 'Aashim Bajracharya',
    'website': 'https://atawah.com',
    'depends': [
        'account',
        'odoo_logger',
        'atawah_purchase_analytic',
        'atawah_amount_discount',
    ],
    'data': [
        'views/account_move.xml',
        'views/product_template.xml',
        'views/account_move_line.xml',
    ],
    'installable': True,
    'auto_install': False,
}
