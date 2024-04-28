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
from odoo import models, fields, api


class SopCancelWizard(models.TransientModel):
    _name = 'sop.cancel.wizard'
    _description = 'Cancel test'

    sop_ids = fields.Many2many('lims.sop')
    cancel_reason = fields.Char('Cancel reason', required=True)
    cancel_dependent_sop = fields.Boolean(string='Cancel dependent SOPs',
                                          help='The cancellation will impact all the tests that are defined as '
                                               'dependent in the test method. If the dependent tests also have '
                                               'dependencies, these are also cancelled')
    depend_sop_ids = fields.Many2many('lims.sop', compute='get_all_depend_sops')

    @api.depends('sop_ids')
    def get_all_depend_sops(self):
        depend_sop_ids = self.sop_ids
        start_sop = depend_sop_ids
        sop_to_remove_after_loops = depend_sop_ids
        while len(start_sop):
            sop_to_remove_after_loops += start_sop
            for sop in start_sop:
                depend_sop_ids += sop.analysis_id.sop_ids.filtered(
                    lambda s: s.rel_type != 'cancel' and
                              sop.method_id in s.method_id.method_ids and
                              s not in depend_sop_ids)
            start_sop = depend_sop_ids.filtered(lambda s: s.name not in sop_to_remove_after_loops.mapped('name'))
        # Remove sops in list self.sop_ids
        self.depend_sop_ids = depend_sop_ids.filtered(lambda s: s.name not in self.sop_ids.mapped('name'))
        return self.depend_sop_ids

    def confirm_cancel(self):
        self.sop_ids.do_cancel(self.cancel_reason)
        if self.cancel_dependent_sop:
            self.depend_sop_ids.do_cancel(self.cancel_reason)
