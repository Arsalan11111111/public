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


class LimsSop(models.Model):
    _inherit = 'lims.sop'

    def check_state_validated(self):
        """
        Method from lims base that validate automatically lims.sop if all results are validated.
        We want to avoid that here
        :return: False
        """
        return False

    def do_validated(self):
        """
        Only allow to validate a sop if all results are validated (or cancelled or reworked)
        :return: super call
        """
        ok_stage_types = ['validated', 'cancel', 'rework']
        results_not_ok = self.result_num_ids.filtered(lambda r: r.rel_type not in ok_stage_types) or \
                         self.result_sel_ids.filtered(lambda rs: rs.rel_type not in ok_stage_types) or \
                         self.result_text_ids.filtered(lambda rt: rt.rel_type not in ok_stage_types) or \
                         self.result_compute_ids.filtered(lambda rc: rc.rel_type not in ok_stage_types)
        if results_not_ok:
            raise exceptions.ValidationError(_("Test can't be validated: not all results are validated."))
        super().do_validated()
