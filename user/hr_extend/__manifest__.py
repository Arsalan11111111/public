# See LICENSE file for full copyright and licensing details.
{
    "name": "Hr Extended",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "license": "LGPL-3",
    "summary": "HR Extended",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "depends": ["base", "hr", "hr_attendance_zktecho", "hr_payroll"],

    "data": [
        'security/hr_extend_security.xml',
        'security/ir.model.access.csv',
        'views/hr_payroll_extend.xml',
        'views/hr_draft_attendance.xml',
        'views/hr_salary_attachment_view.xml',
        'views/hr_description_type_view.xml',
        'views/hr_payslip.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
    ],

    "installable": True,
    "auto_install": False,
}
