# -*- coding: utf-8 -*-
{
    'name': 'Atawah Contact',
    'version': '16.0.0.2',
    'category': 'Contact',
    'sequence': -1,
    'application': True,
    'license': 'OPL-1',
    'summary': 'Features related to contact specific.',
    'description': """
        0.0.1 : Get to add fields to store Terms and conditions and automate in purchase.
        0.0.2 : Get payment related journal items for the partner.

    """,
    'author': 'Aashim Bajracharya',
    'website': 'https://atawah.com',
    'depends': [
        'contacts',
        'purchase',
        'odoo_logger',
        'account'
    ],
    'data': [
        'views/res_partner.xml'
    ],
    'installable': True,
    'auto_install': False,
}
