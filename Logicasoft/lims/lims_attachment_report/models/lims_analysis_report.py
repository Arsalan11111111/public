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


class LimsAnalysisReport(models.Model):
    _inherit = 'lims.analysis.report'

    attachment_ids = fields.Many2many('ir.attachment', string='Publishable attachements', compute='get_attachment_ids')
    attachment_published_count = fields.Integer("Published attachements", compute="get_attachment_ids")
    report_image_attachment_ids = fields.Many2many('ir.attachment', string='Images', compute='get_report_images')
    pictures_count = fields.Integer(compute="get_report_images")

    def get_attachment_ids(self):
        attachment_obj = self.env['ir.attachment']
        all_attachment_ids = attachment_obj.search(
            [('res_id', 'in', self.ids), ('res_model', '=', 'lims.analysis.report')])
        for record in self:
            record.attachment_ids = all_attachment_ids.filtered(lambda a: a.res_id == record.id)
            record.attachment_published_count = len(record.attachment_ids.filtered(lambda a: a.url and a.public))

    def get_public_attachment_ids(self):
        return self.env['ir.attachment'].search(
            [('res_id', 'in', self.ids), ('res_model', '=', 'lims.analysis.report'), ('url', '!=', False),
             ('public', '=', True), ('datas', '!=', False)], order='sequence, id')

    @api.depends('report_analysis_line_ids', 'report_analysis_line_ids.analysis_id')
    def get_report_images(self):
        attachment_obj = self.env['ir.attachment']
        for record in self:
            analysis_ids = self.report_analysis_line_ids.mapped('analysis_id')
            record.report_image_attachment_ids = attachment_obj.search([
                ('res_id', 'in', analysis_ids.ids),
                ('mimetype', 'like', 'image'),
                ('res_model', '=', 'lims.analysis'),
            ])
            record.pictures_count = len(record.report_image_attachment_ids)

    def open_attachment_ids(self):
        self.ensure_one()
        tree = self.env.ref('lims_attachment_report.lims_ir_attachment_report_tree')
        ctx = self.env.context.copy()
        ctx.update({
            'default_res_id': self.id,
            'default_res_model': 'lims.analysis.report',
        })
        return {
            'name': _('Attachment(s) for report : {}'.format(self.name)),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_id': tree.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'domain': [('res_id', '=', self.id), ('res_model', '=', 'lims.analysis.report')],
            'context': ctx,
        }

    def open_analysis_pictures(self):
        self.ensure_one()
        tree = self.env.ref('lims_attachment_report.lims_ir_attachment_tree_no_create')
        ctx = self.env.context.copy()
        ctx.update({
            'default_res_id': self.id,
            'default_res_model': 'lims.analysis.report',
        })
        analysis_ids = self.report_analysis_line_ids.mapped('analysis_id')
        return {
            'name': _('Picture'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_id': tree.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'domain': [
                ('res_id', 'in', analysis_ids.ids), ('mimetype', 'like', 'image'), ('res_model', '=', 'lims.analysis')
            ],
            'context': ctx,
        }

    def get_attachment_for_analysis(self, analysis_id):
        """
        Returns the report attachments linked to a specific analysis (analysis must be present on the report)
        """
        self.ensure_one()
        return self.report_image_attachment_ids.filtered(
            lambda a: a.is_on_report and (a.analysis_id.id == analysis_id.id)
        )
