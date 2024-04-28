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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nb_analysis = fields.Integer(compute='compute_info_analysis', compute_sudo=True)
    nb_result = fields.Integer(compute='compute_info_analysis', compute_sudo=True)
    nb_compute_result = fields.Integer(compute='compute_info_analysis', compute_sudo=True)
    nb_sel_result = fields.Integer(compute='compute_info_analysis', compute_sudo=True)
    nb_text_result = fields.Integer(compute='compute_info_analysis', compute_sudo=True)
    matrix_id = fields.Many2one('lims.matrix', 'Matrix')
    pack_ids = fields.Many2many('lims.parameter.pack', string='Parameter Pack')
    lims_for_analysis = fields.Boolean('Lims For Analysis', help="This is checked to make eligible the product and "
                                                                 "all his variants inside the LIMS flow's process.")

    def compute_info_analysis(self):
        for record in self:
            analysis_ids = self.env['lims.analysis'].search([('product_id.product_tmpl_id', '=', record.id)])
            record.nb_analysis = len(analysis_ids)
            record.nb_result = len(analysis_ids.mapped('result_num_ids'))
            record.nb_compute_result = len(analysis_ids.mapped('result_compute_ids'))
            record.nb_sel_result = len(analysis_ids.mapped('result_sel_ids'))
            record.nb_text_result = len(analysis_ids.mapped('result_text_ids'))

    def get_all_analysis_view(self):
        """
        Open the view analysis where the sampling point is in
        :return:
        """
        return {
            'name': _('Analysis'),
            'domain': [('product_id.product_tmpl_id', '=', self.id)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
        }

    def get_all_analysis_result_view(self):
        """
        Open the view result where the sampling point is in
        :return:
        """
        analysis_ids = self.env['lims.analysis'].search([('product_id.product_tmpl_id', '=', self.id)])
        return {
            'name': _('Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.numeric.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def get_all_analysis_sel_result_view(self):
        """
        Open the view selection result where the sampling point is in
        :return:
        """
        analysis_ids = self.env['lims.analysis'].search([('product_id.product_tmpl_id', '=', self.id)])
        return {
            'name': _('Sel Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.sel.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }

    def get_all_analysis_compute_result_view(self):
        """
        Open the view compute result where the sampling point is in
        :return:
        """
        analysis_ids = self.env['lims.analysis'].search([('product_id.product_tmpl_id', '=', self.id)])
        return {
            'name': _('Compute Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.compute.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot,calendar',
        }

    def get_all_analysis_text_result_view(self):
        analysis_ids = self.env['lims.analysis'].search([('product_id.product_tmpl_id', '=', self.id)])
        return {
            'name': _('Text Result'),
            'domain': [('analysis_id', 'in', analysis_ids.ids)],
            'res_model': 'lims.analysis.text.result',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,calendar',
        }
