# -*- coding: utf-8 -*-

{
    'name': 'Atawah Odoo Reports',
    'version': '16.0.1.5',
    'category': 'Base',
    'sequence': -1,
    'application': True,
    'license': 'OPL-1',
    'summary': 'Customized reports for sales, purchase, invoices, inventory etc.',
    'description': """
        0.0.1: Develop tax invoice pdf layout.
        0.0.2: Fill up the page if the lines count of invoice is less than equal to 5.
        0.0.3: Get 'ref' field as LPO in tax invoice pdf layout.
        0.0.4: Remove last row line of the table.
        0.0.5: Link our ref and project no with tax invoice.
        0.0.6: Reposition the terms and condition in tax invoice.
        0.0.7: Get partner_delivery_address_id and child_delivery_address_id from module
               atawah_purchase_analytic in the tax invoice.
        0.0.8: Resolve merge conflicts.
        0.0.9: Recover Paid stamp.
        0.1.0: Add transperancy to stamp and add project name in the tax invoice layout.
        0.1.1: Group partner ledger journal items by project name.
        0.1.2: Group journal entries by project name.
        0.1.3: Get side lines for the last invoice item in tax invoice pdf layout.
        0.1.4: Fixes in tax invoice report.
        0.1.5: Remove taxes and section subtotal details in sale order pdf layout.
    """,
    'author': 'Aashim Bajracharya',
    'website': 'https://atawah.com',
    'depends': [
        'purchase',
        'account',
        'sales_team',
        'web',
        'odoo_logger',
        'account_reports',
        'atawah_amount_discount'
    ],
    'data': [
        'views/account_move.xml',
        'views/account_move_line.xml',
        'reports/custom_paper_formats.xml',
        'reports/custom_layout.xml',
        'reports/tax_invoice.xml',
        'reports/report_saleorder_document.xml',
    ],
    'installable': True,
    'auto_install': False,
}
