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
from odoo import models, api, exceptions, _


class MassChangeResultWizard(models.TransientModel):
    _inherit = 'mass.change.result.wizard'

    def do_validate(self):
        """
        Completely override method of lims base to call do_validated method on results and not on sops
        (because sops must not be automatically validated)
        """
        if not self.user_has_groups('lims_base.validator1_group'):
            raise exceptions.AccessError(_('You must have extra rights to validate'))
        done_result_ids = self.analysis_result_ids.filtered(lambda r: r.stage_id.type == 'done')
        if done_result_ids:
            done_result_ids.do_validated()
        done_sel_result_ids = self.analysis_sel_result_ids.filtered(lambda r: r.stage_id.type == 'done')
        if done_sel_result_ids:
            done_sel_result_ids.do_validated()
        done_compute_result_ids = self.analysis_compute_result_ids.filtered(lambda r: r.stage_id.type == 'done')
        if done_compute_result_ids:
            done_compute_result_ids.do_validated()
        done_text_result_ids = self.analysis_text_result_ids.filtered(lambda r: r.stage_id.type == 'done')
        if done_text_result_ids:
            done_text_result_ids.do_validated()
