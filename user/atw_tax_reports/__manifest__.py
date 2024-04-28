# -*- coding: utf-8 -*-

{
    'name': 'Tax Reports',
    'version': '16.0.0.5',
    'category': 'Base',
    'sequence': -1,
    'application': True,
    'license': 'OPL-1',
    'summary': 'Custom tax reports',
    'description': """
        16.0.0.1: Add excel tax report.
        16.0.0.2: Add records related to pos, journal entries with tax applied.
        16.0.0.3: Develop vat return report.
        16.0.0.4: Add partner.vat and amount_tax_signed.
        16.0.0.5: Tax Report by Partner
    """,
    'author': 'ATAWAH',
    'website': 'https://atawah.com',
    'depends': [
        'purchase',
        'account',
        'report_xlsx',
        'account_reports',
        'point_of_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/custom_layout.xml',
        'reports/custom_paper_formats.xml',
        'reports/tax_report.xml',
        'reports/vat_return.xml',
        'wizards/tax_report.xml',
        'wizards/vat_return.xml',
        'views/account_move.xml',
        'views/tax_report_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
}
