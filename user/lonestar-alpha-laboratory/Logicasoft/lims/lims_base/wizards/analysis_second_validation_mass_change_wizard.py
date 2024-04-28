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
from odoo import models, fields, api, _, exceptions


class AnalysisSecondValidationMassChangeWizard(models.TransientModel):
    _name = 'analysis.second.validation.mass.change.wizard'
    _description = 'Analysis Second Validation Mass Change Wizard'

    @api.model
    def default_get(self, fields_list):
        analysis_ids = self.env['lims.analysis'].browse(self.env.context.get('default_analysis_ids'))

        res = super(AnalysisSecondValidationMassChangeWizard, self).default_get(fields_list)
        line_ids = []
        for analysis_id in analysis_ids:
            line_ids.append((0, 0, {
                'analysis_id': analysis_id.id,
                'type': analysis_id.stage_id.type,
                'analysis_name': analysis_id.name,
                'analysis_stage_id': analysis_id.stage_id.id,
                'state': analysis_id.state,
                'request_id': analysis_id.request_id.id if analysis_id.request_id else False,
                'sample_name': analysis_id.sample_name,
                'partner_id': analysis_id.partner_id.id if analysis_id.partner_id else False,
            }))
        res.update({'line_ids': line_ids})
        return res

    line_ids = fields.One2many('analysis.second.validation.mass.change.wizard.line', 'link_id', string="Analysis")

    def confirm(self):
        for record in self:
            analysis_not_validated = record.line_ids.mapped('analysis_id').\
                filtered(lambda a: a.stage_id.type not in ['validated1', 'validated2'])
            if analysis_not_validated:
                names = analysis_not_validated.mapped('name')[:10]
                raise exceptions.ValidationError(_('At least one of the selected analyzes is not in '
                                                   'the "validated" status therefore the status cannot be changed. '
                                                   '\n For example : \n {}'.format(', '.join(names))))

            analysis_ids = record.line_ids.mapped('analysis_id').filtered(lambda a: a.stage_id.type == 'validated1')
            analysis_ids.do_validation2()


class AnalysisSecondValidationMassChangeWizardLine(models.TransientModel):
    _name = 'analysis.second.validation.mass.change.wizard.line'
    _description = 'Analysis Second Validation Mass Change Wizard Line'

    def get_type(self):
        return self.env['lims.analysis.stage'].get_analysis_stage_type()

    link_id = fields.Many2one('analysis.second.validation.mass.change.wizard')
    analysis_id = fields.Many2one('lims.analysis')
    type = fields.Selection(selection=get_type)
    analysis_name = fields.Char(string="Analysis's name")
    analysis_stage_id = fields.Many2one('lims.analysis.stage', string="Analysis's stage")
    state = fields.Selection(selection=[
        ('init', 'Init'),
        ('conform', 'Conform'),
        ('not_conform', 'Not Conform'),
        ('unconclusive', 'Inconclusive')
    ], string='State')
    request_id = fields.Many2one('lims.analysis.request')
    sample_name = fields.Char("Sample's name")
    partner_id = fields.Many2one('res.partner')
