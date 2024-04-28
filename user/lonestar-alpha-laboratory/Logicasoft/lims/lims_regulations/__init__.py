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
from . import controllers
from . import models
from . import reports
from . import wizards

from odoo import api, SUPERUSER_ID


def _lims_regulations_post_init(cr, registry):
    """
    Existing analysis will have a regulation_id. We should add this field to field regulation_ids
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    analysis_obj = env['lims.analysis']
    existing_analysis_ids = analysis_obj.search([('regulation_id', '!=', False)])
    for regulation_id in existing_analysis_ids.mapped('regulation_id'):
        analysis_for_regulation = existing_analysis_ids.filtered(lambda a: a.regulation_id == regulation_id)
        # context in case lims_report is installed and some analyses are blocked
        analysis_for_regulation.with_context(bypass_check_locked_analysis=True).write(
            {'regulation_ids': [(4, regulation_id.id)]}
        )
    existing_sample_ids = env['lims.analysis.request.sample'].search([('regulation_id', '!=', False)])
    for regulation_id in existing_sample_ids.mapped('regulation_id'):
        sample_for_regulation = existing_sample_ids.filtered(lambda s: s.regulation_id == regulation_id)
        sample_for_regulation.write({'regulation_ids': [(4, regulation_id.id)]})
