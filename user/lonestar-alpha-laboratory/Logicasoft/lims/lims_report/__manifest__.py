# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################
{
    'name': 'LIMS Report',
    'version': '16.0.1.45',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add analysis reports to the Lims with a validation and publication system.',
    'sequence': 97,
    'description': """
    Lims Report
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_base'],
    'data': [
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/res_config.xml',
        'views/lims_parameter_print.xml',
        'views/lims_parameter_print_group.xml',
        'views/lims_analysis_report.xml',
        'views/lims_analysis_report_line.xml',
        'views/lims_analysis_report_template.xml',
        'views/lims_analysis_request.xml',
        'views/lims_laboratory.xml',
        'views/lims_analysis.xml',
        'views/lims_analysis_result.xml',
        'views/lims_analysis_sel_result.xml',
        'views/lims_analysis_text_result.xml',
        'views/lims_analysis_compute_result.xml',
        'views/lims_parameter_pack.xml',
        'views/lims_sop.xml',
        'views/lims_method_parameter_characteristic.xml',
        'views/lims_parameter.xml',
        'views/lims_analysis_report_tag.xml',
        'views/lims_analysis_report_section.xml',

        'views/lims_portal_report.xml',
        'views/lims_portal_request.xml',
        'views/lims_portal_analysis.xml',

        'reports/external_layout_bold.xml',
        'reports/lims_analysis_report_report.xml',
        'reports/lims_analysis_report_report_board.xml',
        'reports/lims_analysis_report_report_board_vertical.xml',
        'reports/lims_analysis_report_email_template.xml',
        'reports/lims_analysis_report.xml',
        'reports/lims_analysis_detailed_worksheet.xml',
        'reports/lims_sop_worksheet.xml',
        'reports/lims_batch_worksheet_parameters.xml',

        'wizards/create_report_wizard.xml',
        'wizards/report_mass_change.xml',
        'wizards/wizard_confirmation_create_report.xml',
        'wizards/wizard_confirmation_create_report_request.xml',
        'wizards/wizard_group_report.xml',
        'wizards/cancel_report_wizard.xml',
        'wizards/do_sop_is_null_wizard.xml',
        'wizards/mail_compose_message.xml',

        'data/data.xml',

    ],
    'demo': [
        'demo/lims_demo_parameter_print_group.xml',
        'demo/lims_demo_parameter_print.xml',
        'demo/lims_demo_method_parameter_characteristic.xml',
        'demo/lims_demo_analysis_report.xml',
        'demo/lims_demo_analysis_report_line.xml',
        'demo/lims_demo_laboratory.xml',
        'demo/lims_demo_data_user.xml',

    ],
    'assets': {
        'web.assets_backend': [
            '/lims_report/static/src/js/mail_chatter.js',
        ]
    },
    'css': [],
    'test': [],
    'installable': True,
}
