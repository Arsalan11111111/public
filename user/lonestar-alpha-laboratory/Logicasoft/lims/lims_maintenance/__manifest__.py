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
    'name': 'LIMS Maintenance',
    'version': '16.0.1.2',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add traceability to analyses, tests, batches to link them with laboratory equipment.',
    'sequence': 98,
    'description': """
    LIMS Maintenance : you can assign equipment for laboratory measurements.
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_base', 'maintenance'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/lims_analysis_compute_result.xml',
        'views/lims_analysis_result.xml',
        'views/lims_analysis_sel_result.xml',
        'views/lims_batch.xml',
        'views/lims_batch_equipment.xml',
        'views/lims_method_parameter_characteristic.xml',
        'views/lims_method_parameter_characteristic_equipment.xml',
        'views/lims_sop.xml',
        'views/maintenance_equipment.xml',
        'views/lims_method.xml',
        'views/equipment_traceability_type.xml',
        'views/lims_analysis_text_result.xml',
        'views/gamp_category.xml',

        'wizards/sop_mass_change_wizard.xml',
        'wizards/lims_history.xml',
    ],
    'css': [],
    'demo': [
        "demo/maintenance_res_users.xml",
        "demo/maintenance_equipment_traceability_type.xml",
    ],
    'test': [],
    'installable': True,
}
