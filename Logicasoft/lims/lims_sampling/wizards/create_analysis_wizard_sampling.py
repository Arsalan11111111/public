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
from odoo import fields, models, api, _, exceptions


class CreateAnalysisWizard(models.TransientModel):
    _name = 'create.analysis.wizard.sampling'
    _description = 'Analysis Sampling Wizard'

    def get_default_laboratory(self):
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    date_plan = fields.Datetime('Date Plan', required=True)
    date_sample = fields.Datetime('Date Sample')
    partner_id = fields.Many2one('res.partner', 'Partner')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', required=True, default=get_default_laboratory)
    reason_id = fields.Many2one('lims.analysis.reason', 'Reason')
    line_ids = fields.One2many('create.analysis.wizard.sampling.line', 'wizard_id', 'Lines')
    category_id = fields.Many2one('lims.analysis.category', 'Category')

    @api.onchange('laboratory_id')
    def onchange_laboratory_id(self):
        if self.laboratory_id:
            self.line_ids.filtered(lambda l: not l.category_id).update({
                'category_id': self.laboratory_id.default_analysis_category_id.id
            })

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            self.line_ids.update({'category_id': self.category_id.id})

    @api.onchange('reason_id')
    def onchange_reason_id(self):
        if self.reason_id:
            self.line_ids.update({'reason_id': self.reason_id.id})

    def do_create_analysis(self):
        analysis_obj = self.env['lims.analysis']
        vals = {
            'laboratory_id': self.laboratory_id.id,
            'date_plan': self.date_plan,
            'date_sample': self.date_sample,
        }
        for line_id in self.line_ids:
            copy_vals = vals.copy()
            copy_vals.update({
                'sampling_point_id': line_id.sampling_point_id.id,
                'location_id': line_id.sampling_point_id.location_id.id,
                'matrix_id': line_id.sampling_point_id.matrix_id and line_id.sampling_point_id.matrix_id.id or False,
                'regulation_id': (line_id.sampling_point_id.regulation_id
                                  and line_id.sampling_point_id.regulation_id.id or False),
                'category_id': line_id.category_id and line_id.category_id.id,
                'sampling_type_id': line_id.sampling_point_id.sampling_type_id and line_id.sampling_point_id.sampling_type_id.id,
                'reason_id': line_id.reason_id.id if line_id.reason_id else False,
            })
            if line_id.sampling_point_id.partner_id:
                copy_vals['partner_id'] = line_id.sampling_point_id.partner_id.id
            elif self.partner_id:
                copy_vals['partner_id'] = self.partner_id.id
            copies = []
            for i in range(abs(line_id.quantity)):
                copies.append(copy_vals.copy())
            analysis_obj += analysis_obj.create(copies)
        analysis_obj.create_sop()
        return {
            'name': _('Analysis'),
            'view_mode': 'tree,form,pivot,graph,calendar',
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', analysis_obj.ids)]
        }

    @api.model
    def default_get(self, fields_list):
        """
        Autofill the line_ids with sampling point ids
        :param fields_list:
        :return:
        """
        res = super(CreateAnalysisWizard, self).default_get(fields_list)
        sampling_point_ids = self.env['lims.sampling.point'].browse(self.env.context.get('active_ids'))
        if sampling_point_ids.filtered(lambda s: not s.matrix_id):
            raise exceptions.ValidationError(_(
                "Impossible to create an analysis : some sampling points don't have a matrix configured"))
        line_ids = [(0, 0, {
            'sampling_point_id': act_id.id,
            'wizard_id': self.id}) for act_id in sampling_point_ids]
        res.update({'line_ids': line_ids})
        return res


class CreateAnalysisWizardLine(models.TransientModel):
    _name = 'create.analysis.wizard.sampling.line'
    _description = 'Analysis Sampling Wizard Line'

    wizard_id = fields.Many2one('create.analysis.wizard.sampling')
    sampling_point_id = fields.Many2one('lims.sampling.point')
    category_id = fields.Many2one('lims.analysis.category', 'Category')
    reason_id = fields.Many2one('lims.analysis.reason', 'Reason')
    quantity = fields.Integer(string='Quantity', default=1)

