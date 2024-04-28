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
    'name': 'LIMS Tour',
    'version': '16.0.1.11',
    'license': 'Other proprietary',
    'category': 'LIMS',
    'summary': 'addon: Add tour management in Lims.',
    'sequence': 98,
    'description': 'LIMS Tour',
    'author': 'LogicaSoft SPRL',
    'depends': ['lims_sampling'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',

        'views/menuitem.xml',
        'views/lims_analysis.xml',
        'views/lims_sampler_team.xml',
        'views/lims_tour.xml',
        'views/lims_tour_line.xml',
        'views/lims_laboratory.xml',
        'views/lims_tour_name.xml',
        'views/lims_sampling_point.xml',
        'views/lims_sop.xml',
        'views/lims_method.xml',
        'views/lims_analysis_compute_result.xml',
        'views/lims_analysis_numeric_result.xml',
        'views/lims_analysis_sel_result.xml',
        'views/lims_analysis_text_result.xml',

        'views/lims_portal_tour.xml',
        'views/lims_portal_analysis.xml',

        'wizards/duplicate_tour_wizard.xml',
        'wizards/create_tour_wizard.xml',
        'wizards/create_analysis_wizard_sampling.xml',
        'wizards/tour_cancel_wizard.xml',
    ],
    'css': [],
    'demo': [
        'demo/lims_demo_tour_name.xml',
        'demo/lims_demo_sampler_team.xml',
        'demo/lims_demo_tour.xml',
        'demo/lims_demo_data_user.xml',
        'demo/lims_demo_method.xml',
        'demo/lims_demo_data_laboratory.xml',
    ],
    'test': [],
    'installable': True,
}
