# -*- coding: utf-8 -*-
{
    'name': "Extend Atawah Purchase Analytic",
    'summary': """
        Extension of features of atawah_purchase_analytic
    """,

    'description': """
        0.0.1: - Add header for secondary delivery address in bank recon list view.
               - Get analytic accounts in bank reconcilication list view.
        0.0.2: - Get delivery addresses from invoice to payment.
        0.0.3: - Get delivery addresses from bank recon to journal items (fields are in atw_account_features)
    """,

    'author': "Atawah SPC",
    'website': "https://www.atawah.com..",
    'category': 'Accounting',
    'version': '16.0.0.3',
    'depends': [
        'base',
        'purchase',
        'account',
        'atawah_purchase_analytic',
        'account_payment',
        'atw_account_features'
    ],
    'data': [
        'views/account_bank_statement_line.xml',
    ],
    'sequence': -1,
    'application': True
}
