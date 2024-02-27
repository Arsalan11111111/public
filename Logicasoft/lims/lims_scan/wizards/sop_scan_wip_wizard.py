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
from odoo import models, fields, api, exceptions, _


class SopScanWipWizard(models.TransientModel):
    _name = 'sop.scan.wip.wizard'
    _description = 'Test Scan Wip Wizard'
    _inherit = ['sop.scan.wizard']

    line_ids = fields.One2many('sop.scan.wip.wizard.line', 'wizard_id', 'Test')

    def create_lines(self, sop_id):
        if sop_id.rel_type not in ['todo', 'wip']:
            self.error_message = _('You can only pass in WIP stage test in "todo" or "WIP" stages')
        else:
            wip_stage = self.env['lims.method.stage'].search([('method_ids', '=', sop_id.method_id.id),
                                                              ('type', '=', 'wip')], limit=1)
            if not self.line_ids.filtered(lambda s: s.sop_id == sop_id):
                self.line_ids += self.env['sop.scan.wip.wizard.line'].new({
                    'sop_id': sop_id.id,
                    'next_stage_id': sop_id.next_wip_stage or wip_stage,
                })

    def do_confirm(self):
        if self.line_ids:
            self.line_ids.mapped('sop_id').do_next_stage()
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'lims.sop',
                'domain': [('id', 'in', self.line_ids.mapped('sop_id').ids)],
                'name': 'Test'
            }


class SopScanWipWizardLine(models.TransientModel):
    _name = 'sop.scan.wip.wizard.line'
    _description = 'Test Scan Wip Wizard Line'

    wizard_id = fields.Many2one('sop.scan.wip.wizard')
    sop_id = fields.Many2one('lims.sop', 'Test')
    next_stage_id = fields.Many2one('lims.method.stage', 'Next Stage')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', related='sop_id.analysis_id')
    method_id = fields.Many2one('lims.method', related='sop_id.method_id')
