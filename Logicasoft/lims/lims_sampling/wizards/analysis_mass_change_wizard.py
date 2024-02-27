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


class AnalysisMassChangeWizard(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard'

    sampling_type_id = fields.Many2one('lims.sampling.type', 'Sampling type')

    @api.model
    def default_get(self, fields_list):
        res = super(AnalysisMassChangeWizard, self).default_get(fields_list)
        for line in res['line_ids']:
            analysis_id = self.env['lims.analysis'].browse(line[2]['analysis_id'])
            line[2].update({
                'sampling_type_id': analysis_id.sampling_type_id.id
            })
        return res

    @api.onchange('sampling_type_id')
    def onchange_sampling_type_id(self):
        if self.sampling_type_id:
            self.line_ids.update({'sampling_type_id': self.sampling_type_id.id})

    def save_analysis(self):
        res = super(AnalysisMassChangeWizard, self).save_analysis()

        sampling_type_ids = self.line_ids.mapped('sampling_type_id')
        for sampling_type_id in sampling_type_ids:
            self.line_ids.filtered(lambda l: l.sampling_type_id == sampling_type_id).mapped('analysis_id').write({
                'sampling_type_id': sampling_type_id.id
            })

        return res


class AnalysisMassChangeWizardLine(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard.line'

    sampling_type_id = fields.Many2one('lims.sampling.type', 'Sampling type')
