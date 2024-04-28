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
from odoo import models, fields, api


class AnalysisMassChangeWizard(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard'

    reception_temperature = fields.Char()

    @api.model
    def default_get(self, fields_list):
        """
        Generate line_ids from context.active_ids
        :param fields_list:
        :return:
        """
        res = super(AnalysisMassChangeWizard, self).default_get(fields_list)
        analysis_obj = self.env['lims.analysis']
        for line_id in res.get('line_ids'):
            analysis_id = analysis_obj.browse(line_id[2].get('analysis_id'))
            line_id[2].update({
                'reception_temperature': analysis_id.reception_temperature
            })
        return res

    @api.onchange('reception_temperature')
    def onchange_reception_temperature(self):
        if self.reception_temperature:
            self.line_ids.update({
                'reception_temperature': self.reception_temperature
            })

    def save_analysis(self):
        super(AnalysisMassChangeWizard, self).save_analysis()
        for line in self.line_ids.filtered(lambda l: l.reception_temperature):
            line.analysis_id.reception_temperature = line.reception_temperature


class AnalysisMassChangeWizardLine(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard.line'

    reception_temperature = fields.Char()
