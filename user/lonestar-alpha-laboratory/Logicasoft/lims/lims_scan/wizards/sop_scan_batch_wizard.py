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
from odoo import models, fields, _


class SopScanBatchWizard(models.TransientModel):
    _name = 'sop.scan.batch.wizard'
    _description = 'Test Scan Batch Wizard'
    _inherit = ['sop.scan.wizard']

    line_ids = fields.One2many('sop.scan.batch.wizard.line', 'wizard_id', 'Test')
    department_id = fields.Many2one('lims.department')

    def create_lines(self, sop_id):
        if sop_id.batch_id:
            self.error_message = _(
                'SOP : {}, is already assigned to a batch : {}').format(self.sop_name, sop_id.batch_id.name)
        elif self.department_id and self.department_id != sop_id.department_id:
            self.error_message = _(
                'SOP : {}, is assigned to the department : {}, from the laboratory : {}').format(
                self.sop_name, sop_id.department_id.name, sop_id.labo_id.name)
        elif sop_id.rel_type not in ['todo', 'plan']:
            self.error_message = _("You can only create batch from sops with 'todo' or 'planned' states "
                                   "({} is {})").format(self.sop_name, sop_id.stage_id.name)
        elif not self.line_ids.filtered(lambda s: s.sop_id == sop_id):
            self.line_ids += self.env['sop.scan.batch.wizard.line'].new({
                'sop_id': sop_id.id,
            })
            self.department_id = sop_id.department_id

    def do_confirm(self):
        if self.line_ids:
            batch_ids = self.line_ids.mapped('sop_id').create_batch()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'lims.batch',
                'domain': [('id', '=', batch_ids.ids)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'name': 'Batch'
            }


class SopScanBatchWizardLine(models.TransientModel):
    _name = 'sop.scan.batch.wizard.line'
    _description = 'Test Scan Batch Wizard Line'

    wizard_id = fields.Many2one('sop.scan.batch.wizard')
    sop_id = fields.Many2one('lims.sop', 'Test')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', related='sop_id.analysis_id')
    method_id = fields.Many2one('lims.method', related='sop_id.method_id')
    rel_batch_id = fields.Many2one('lims.batch', related='sop_id.batch_id')
    rel_department_id = fields.Many2one('lims.department', related='sop_id.department_id')
    rel_labo_id = fields.Many2one('lims.laboratory', related='sop_id.labo_id')
