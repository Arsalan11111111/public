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
from odoo import http, _
from odoo.http import request


class LimsBarcodeController(http.Controller):

    @http.route('/lims_scan_advanced/scan_from_main_menu', type='json', auth='user')
    def main_menu(self, barcode, **kw):
        if barcode and barcode == 'O-CMD.SRCP':
            action_form = request.env.ref('lims_scan.sop_scan_receipt_action').sudo().read()[0]
            return {'action': action_form}
        elif barcode and barcode == 'O-CMD.SWIP':
            action_form = request.env.ref('lims_scan.sop_scan_wip_wizard_action').sudo().read()[0]
            return {'action': action_form}
        elif barcode and barcode == 'O-CMD.BCRE':
            action_form = request.env.ref('lims_scan.sop_scan_batch_wizard_action').sudo().read()[0]
            return {'action': action_form}
        return False
