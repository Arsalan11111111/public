# -*- coding: utf-8 -*-
{
    'name': 'Purchase Reports',
    'summary': '',
    'description': '''
        - Modified the reports to have the signature section on bottomost part of pdf of PO.
        - Modified the header section of custom purchase report.
        - Fix purchase report vendor details section.
        - Fix repeating table header in po report.
    ''',
    'author': 'Younis Mostafa Khalaf',
    'website': '',
    'category': 'Purchase',
    'version': '16.0.1.0.4',
    'license': 'OPL-1',
    'depends': [
        'base',
        'purchase',
        'purchase_discount',
        'atawah_purchase_analytic',
        'atw_reports',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'report/purchase_template.xml',
        'report/reports.xml',
        # 'views/res_partner.xml',
        'views/res_company.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': -1,
    'auto_install': False,
}
