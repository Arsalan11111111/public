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
from odoo import fields, models, api, exceptions, _


class LimsAnalysisReport(models.Model):
    _inherit = 'lims.analysis.report'

    lot_ids = fields.One2many('stock.lot', 'report_id')
    is_report_validator = fields.Boolean('Report validator', default=False, compute='compute_is_report_validator')

    def print_report(self):
        res = super().print_report()
        if 'print_from_stock_lot' in self.env.context:
            context_str = '{'+"\"print_from_stock_lot\": {0}".format(
                self.env.context.get('print_from_stock_lot'))+'}'
            return {
                'type': 'ir.actions.act_url',
                'url': '/report/pdf/{0}/{1}?{2}'.format(
                    self.report_id.report_name,
                    self.id,
                    'context={}'.format(context_str)
                ),
                'target': 'new',
            }
        return res

    def compute_is_report_validator(self):
        is_report_validator = self.env.user.has_group('lims_report.group_lims_validate_report') or False
        for record in self:
            record.is_report_validator = is_report_validator
