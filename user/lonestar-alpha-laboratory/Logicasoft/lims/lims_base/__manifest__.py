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
    'name': 'LIMS Base',
    'version': '16.0.2.48',
    'license': 'Other proprietary',
    'category': 'LIMS/base',
    'summary': 'Core module to run the Lims on this server.',
    'sequence': 96,
    'author': 'LogicaSoft SPRL',
    'depends': ['product', 'hr', 'portal', 'mail_tracking_relational_values'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'wizards/analysis_cancel_wizard.xml',
        'wizards/sop_cancel_wizard.xml',
        'wizards/sop_rework_wizard.xml',
        'wizards/request_cancel_wizard.xml',
        'wizards/mass_change_result_wizard.xml',
        'wizards/create_parameter_pack_wizard.xml',
        'wizards/result_rework_wizard.xml',
        'wizards/result_cancel_wizard.xml',
        'wizards/batch_mass_change_wizard.xml',
        'wizards/sop_duplicate_reason_wizard.xml',

        'views/menuitem.xml',
        'views/lims_accreditation.xml',
        'views/lims_analysis.xml',
        'views/lims_analysis_category.xml',
        'views/lims_analysis_reason.xml',
        'views/lims_analysis_request.xml',
        'views/lims_analysis_request_sample.xml',
        'views/lims_analysis_request_tags.xml',
        'views/lims_analysis_sel_result.xml',
        'views/lims_analysis_numeric_result.xml',
        'views/lims_analysis_stage.xml',
        'views/lims_batch.xml',
        'views/lims_department.xml',
        'views/lims_laboratory.xml',
        'views/lims_matrix.xml',
        'views/lims_matrix_type.xml',
        'views/lims_method.xml',
        'views/lims_method_parameter_characteristic.xml',
        'views/lims_parameter_type.xml',
        'views/lims_parameter.xml',
        'views/lims_parameter_pack.xml',
        'views/lims_parameter_pack_line.xml',
        'views/lims_regulation.xml',
        'views/lims_request_category.xml',
        'views/lims_result_stage.xml',
        'views/lims_result_value.xml',
        'views/lims_standard.xml',
        'views/lims_sop.xml',
        'views/lims_method_stage.xml',
        'views/res_partner.xml',
        'views/res_config.xml',
        'views/lims_batch_operator.xml',
        'views/res_users.xml',
        'views/lims_analysis_compute_result.xml',
        'views/lims_parameter_compute_correspondence.xml',
        'views/lims_attribute_type.xml',
        'views/lims_analysis_tag.xml',
        'views/hr_employee.xml',
        'views/lims_analysis_limit_result.xml',
        'views/lims_work_instruction.xml',
        'views/lims_result_log.xml',
        'views/lims_method_parameter_characteristic_limit.xml',
        'views/lims_analytical_technique.xml',
        'views/lims_analysis_text_result.xml',
        'views/lims_parameter_pack_tag.xml',
        'views/lims_parameter_pack_line_item.xml',
        'views/product_template.xml',
        'views/lims_method_attribute.xml',
        'views/lims_method_container.xml',
        'views/lims_method_attribute_category.xml',
        'views/lims_request_product_pack.xml',
        'views/lims_result_compute_correspondence.xml',
        'views/product_product.xml',

        'views/lims_portal_request.xml',
        'views/lims_portal_analysis.xml',

        'wizards/add_parameters_wizard.xml',
        'wizards/add_parameters_request.xml',
        'wizards/print_qweb_label_wizard.xml',
        'wizards/print_qweb_container_wizard.xml',
        'wizards/create_batch_wizard.xml',
        'wizards/request_mass_change_wizard.xml',
        'wizards/analysis_mass_change_wizard.xml',
        'wizards/sop_mass_change_wizard.xml',
        'wizards/do_sop_is_null_wizard.xml',
        'wizards/create_analysis_wizard.xml',
        'wizards/add_parameters_request_product.xml',
        'wizards/parameter_characteristic_duplicate_wizard.xml',
        'wizards/parameter_compute_correspondence_wizard.xml',
        'wizards/sel_result_mass_change_wizard.xml',
        'wizards/analysis_second_validation_mass_change_wizard.xml',
        'wizards/lims_history.xml',

        'reports/layout.xml',
        'reports/paper_format.xml',
        'reports/sop_report.xml',
        'reports/lims_sop_worksheet.xml',
        'reports/container_report.xml',
        'reports/lims_analysis_report.xml',
        'reports/lims_analysis_request_report.xml',
        'reports/lims_analysis_worksheet.xml',
        'reports/lims_analysis_detailed_worksheet.xml',
        'reports/lims_batch_worksheet.xml',
        'reports/lims_batch_worksheet_parameters.xml',
        'reports/lims_analysis_worksheet_parameters.xml',

        'data/ir_sequence.xml',
        'data/data.xml',
        'data/ir_actions_server.xml',
        'data/ir_cron.xml',
        'data/mail_template.xml',
    ],
    'demo': [
        "demo/lims_demo_res_users.xml",
        'demo/lims_demo_data_laboratory.xml',
        'demo/lims_demo_res_partner.xml',
        'demo/lims_demo_data_user.xml',
        'demo/lims_demo_result_stage.xml',
        'demo/lims_demo_data_department.xml',
        'demo/lims_demo_standard.xml',
        'demo/lims_demo_regulation.xml',
        'demo/lims_demo_accreditation.xml',
        'demo/lims_demo_matrix_type.xml',
        'demo/lims_demo_matrix.xml',
        'demo/lims_demo_parameter_type.xml',
        'demo/lims_demo_method.xml',
        'demo/lims_demo_result_value.xml',
        'demo/lims_demo_parameter.xml',
        'demo/lims_demo_method_parameter_characteristic.xml',
        'demo/lims_demo_parameter_pack_line.xml',
        'demo/lims_demo_parameter_pack.xml',
        'demo/lims_demo_analysis.xml',
        'demo/lims_demo_data_analysis_request.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/lims_base/static/src/js/parameters_helper.js',
            '/lims_base/static/src/js/core/domain.js',
            '/lims_base/static/src/scss/parameters_helper.scss',
            '/lims_base/static/src/scss/lims_base.scss',
            '/lims_base/static/src/**/*.xml',
        ]
    },
    'css': [],
    'test': [],
    'application': True,
    'installable': True,
}
