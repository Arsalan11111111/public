# -*- coding: utf-8 -*-
##############################################################################
#
#     Odoo Proprietary License v1.0
#     This software and associated files (the "Software") may only be used (executed,
#     modified, executed after modifications) if you have purchased a valid license
#     from the authors, typically via Odoo Apps, or if you have received a written
#     agreement from the authors of the Software (see the COPYRIGHT file).
#     You may develop Odoo modules that use the Software as a library (typically
#     by depending on it, importing it and using its resources), but without copying
#     any source code or material from the Software. You may distribute those
#     modules under the license of your choice, provided that this license is
#     compatible with the terms of the Odoo Proprietary License (For example:
#     LGPL, MIT, or proprietary licenses similar to this one).
#     It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#     or modified copies of the Software.
#     The above copyright notice and this permission notice must be included in all
#     copies or substantial portions of the Software.
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#     IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#     DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#     ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.
#
##############################################################################
from odoo import models, api
import base64


class SopScanReceiptWizard(models.TransientModel):
    _inherit = 'sop.scan.receipt.wizard'

    def do_confirm(self):
        res = super(SopScanReceiptWizard, self).do_confirm()
        analysis_ids = self.line_ids.mapped('sop_id').mapped('analysis_id')
        not_ok_analysis_ids = analysis_ids.filtered(lambda a: a.sop_ids.filtered(lambda s: s.rel_type != 'todo'))
        if not_ok_analysis_ids:
            report_id = self.env.ref('lims_scan_report.report_scan_anomaly_action')
            action = report_id.report_action(not_ok_analysis_ids)
            action.update({
                'report_type': 'qweb-html'
            })
            return action
        return res
