# -*- coding: utf-8 -*-
{
    'name': 'Atawah Purchase Features',
    'version': '16.0.0.3',
    'category': 'Purchase',
    'sequence': -1,
    'application': True,
    'license': 'OPL-1',
    'summary': 'Features related to purchase specific.',
    'description': """
        0.0.1 : Automate analytic accounts in each line when filled in the main section of purchase
        0.0.2 : Need approval level by the group of users for the RFQ for amount greater than 500.
        0.0.3 : Get a switch controller in company for the feature of multi rfq approval.

    """,
    'author': 'Aashim Bajracharya',
    'website': 'https://atawah.com',
    'depends': [
        'purchase',
        'odoo_logger',
    ],
    'data': [
        'security/res_groups.xml',
        'views/res_company.xml',
        'views/purchase.xml',
    ],
    'installable': True,
    'auto_install': False,
}
