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
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    request_count = fields.Integer(compute='get_request_count',
                                   help='List of all analysis requests that are personally assigned to it.')
    analysis_count = fields.Integer(compute='get_request_count',
                                    help='List of all the analysis which are personally attributed to it.')

    def get_request_count(self):
        if self.ids:
            request_counted_data = self.env['lims.analysis.request'].read_group([('active', '=', True), ('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
            request_mapped_data = { count['partner_id'][0]: count['partner_id_count'] for count in request_counted_data }
            analysis_counted_data = self.env['lims.analysis'].read_group([('active', '=', True), ('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
            analysis_mapped_data = { count['partner_id'][0]: count['partner_id_count'] for count in analysis_counted_data }
        else:
            request_mapped_data = {}
            analysis_mapped_data = {}

        for record in self:
            record.request_count = request_mapped_data.get(record.id, 0)
            record.analysis_count = analysis_mapped_data.get(record.id, 0)

    def open_analysis_request(self):
        return {
            'name': _('Analysis Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis.request',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
        }

    def open_analysis(self):
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
        }
