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
from odoo import fields, models, api
import uuid


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def compute_analysis(self):
        analysis_obj = self.env['lims.analysis']

        for record in self:
            if record.res_model == 'lims.analysis' and record.res_id:
                record.analysis_id = analysis_obj.browse(record.res_id)
            else:
                record.analysis_id = False

    analysis_id = fields.Many2one('lims.analysis', string='Analysis', compute=compute_analysis)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'public' in vals and vals.get('res_model') == 'lims.analysis.report' and not vals.get('url'):
                vals['url'] = f'/{self._generate_url()}'
        return super(IrAttachment, self).create(vals_list)

    def write(self, vals):
        for record in self:
            res_model = vals.get('res_model') or record.res_model or False
            public = vals.get('public') or record.public or False
            url = vals.get('url') or record.url or False
            if res_model == 'lims.analysis.report' and public and not url:
                vals['url'] = f'/{record._generate_url()}'
        return super(IrAttachment, self).write(vals)

    def _generate_url(self):
        return uuid.uuid4()

