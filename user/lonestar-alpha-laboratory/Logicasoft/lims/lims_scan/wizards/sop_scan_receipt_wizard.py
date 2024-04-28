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


class SopScanReceiptWizard(models.TransientModel):
    _name = 'sop.scan.receipt.wizard'
    _description = 'Test scan receipt wizard'
    _inherit = ['sop.scan.wizard']

    line_ids = fields.One2many('sop.scan.receipt.wizard.line', 'wizard_id', 'Test')

    def get_authorized_stages(self):
        """
        Return stages in which sops can be to authorized reception scan
        (In a separated function to ease inheritance)
        """
        return ['draft', 'plan']

    def create_lines(self, sop_id):
        existing_line = self.line_ids.filtered(lambda s: s.sop_id == sop_id)
        if existing_line:
            existing_line.update({
                'nb_scan': existing_line.nb_scan + 1
            })
        else:
            authorized_stages = self.get_authorized_stages()
            if sop_id.rel_type in authorized_stages:
                self.line_ids += self.env['sop.scan.receipt.wizard.line'].new({
                    'sop_id': sop_id.id,
                    'nb_scan': sop_id.nb_label + 1,
                })
            else:
                self.error_message = _(
                    "{} is in stage {}. Authorized staged are {}.").format(
                        sop_id.name, sop_id.stage_id.name, ', '.join(authorized_stages))

    def do_confirm(self):
        analysis_ids = self.mapped('line_ids').mapped('sop_id').mapped('analysis_id') \
            .filtered(lambda a: not a.date_sample_receipt)
        if analysis_ids:
            analysis_ids.write({
                'date_sample_receipt': fields.Datetime.now(),
            })
        for line_id in self.line_ids:
            line_id.sop_id.write({
                'nb_label': line_id.nb_scan,
                'is_incomplete': line_id.nb_scan < line_id.nb_label_total,
            })
        self.mapped('line_ids').mapped('sop_id').with_context(sop_no_todo=True).do_todo()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lims.sop',
            'domain': [('id', 'in', self.line_ids.mapped('sop_id').ids)],
            'name': 'Test'
        }


class SopScanReceiptWizardLine(models.TransientModel):
    _name = 'sop.scan.receipt.wizard.line'
    _description = 'Test scan receipt wizard line'

    wizard_id = fields.Many2one('sop.scan.receipt.wizard')
    sop_id = fields.Many2one('lims.sop', 'Test')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', related='sop_id.analysis_id')
    method_id = fields.Many2one('lims.method', related='sop_id.method_id')
    nb_label_total = fields.Integer('Nb label waited for', related='sop_id.method_id.nb_label_total')
    nb_scan = fields.Integer('Nb label scanned')
