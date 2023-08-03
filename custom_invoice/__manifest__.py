# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    "name": "Custom Invoice",
    "version": "16.0.1.0",

    "author": "Kanak Infosystems LLP.",
    "website": "https://www.kanakinfosystems.com",
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "data/report_paperformat.xml",
        "report/account_report.xml",
        "views/invoice_report.xml",
        "views/invoice_view.xml",
        "views/res_company.xml",
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
