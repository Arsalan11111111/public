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
from odoo import models, fields, api, _


class ResultCancelWizard(models.TransientModel):
    _name = 'result.cancel.wizard'
    _description = 'Cancel Result'

    def create_line_ids(self,):
        result_sel_ids = self.env['lims.analysis.sel.result']
        result_ids = self.env['lims.analysis.numeric.result']
        result_compute_ids = self.env['lims.analysis.compute.result']
        result_text_ids = self.env['lims.analysis.text.result']
        line_ids = line_obj = self.env['result.cancel.wizard.line']
        if self.env.context.get('default_result_ids'):
            result_ids = self.env['lims.analysis.numeric.result'].browse(self.env.context.get('default_result_ids'))
        if self.env.context.get('default_result_sel_ids'):
            result_sel_ids = self.env['lims.analysis.sel.result'].browse(self.env.context.get('default_result_sel_ids'))
        if self.env.context.get('default_result_compute_ids'):
            result_compute_ids = self.env['lims.analysis.compute.result'].browse(self.env.context.get('default_result_compute_ids'))
        if self.env.context.get('default_result_text_ids'):
            result_text_ids = self.env['lims.analysis.text.result'].browse(
                self.env.context.get('default_result_text_ids'))
        for result in result_ids:
            line_ids += line_obj.new({'result_id': result.id, 'name': result.method_param_charac_id.tech_name})
        for result_sel in result_sel_ids:
            line_ids += line_obj.new({'result_sel_id': result_sel.id, 'name': result_sel.method_param_charac_id.tech_name})
        for result_compute in result_compute_ids:
            line_ids += line_obj.new({'result_compute_id': result_compute.id, 'name': result_compute.method_param_charac_id.tech_name})
        for result_text in result_text_ids:
            line_ids += line_obj.new({
                'result_text_id': result_text.id,
                'name': result_text.method_param_charac_id.tech_name
            })
        return line_ids

    line_ids = fields.One2many('result.cancel.wizard.line', 'wizard_id', default=create_line_ids)
    reason = fields.Char('Reason')

    def confirm_cancel(self):
        analysis_ids = self.env['lims.analysis']
        if self.line_ids.mapped('result_id'):
            self.line_ids.mapped('result_id').do_cancel()
            analysis_ids += self.line_ids.mapped('result_id').mapped('analysis_id')
        if self.line_ids.mapped('result_sel_id'):
            self.line_ids.mapped('result_sel_id').do_cancel()
            analysis_ids += self.line_ids.mapped('result_sel_id').mapped('analysis_id')
        if self.line_ids.mapped('result_compute_id'):
            self.line_ids.mapped('result_compute_id').do_cancel()
            analysis_ids += self.line_ids.mapped('result_sel_id').mapped('analysis_id')
        if self.line_ids.mapped('result_text_id'):
            self.line_ids.mapped('result_text_id').do_cancel()
            analysis_ids += self.line_ids.mapped('result_text_id').mapped('analysis_id')
        for result in self.line_ids.mapped('result_id'):
            result.analysis_id.message_post(body=_('Result {} cancelled by {}. Reason: {}')
                                            .format(result.method_param_charac_id.tech_name, self.env.user.name,
                                                    self.reason))
        for result in self.line_ids.mapped('result_sel_id'):
            result.analysis_id.message_post(body=_('Result {} cancelled by {}. Reason: {}')
                                            .format(result.method_param_charac_id.tech_name, self.env.user.name,
                                                    self.reason))
        for result in self.line_ids.mapped('result_compute_id'):
            result.analysis_id.message_post(body=_('Result {} cancelled by {}. Reason: {}')
                                            .format(result.method_param_charac_id.tech_name, self.env.user.name,
                                                    self.reason))
        for result in self.line_ids.mapped('result_text_id'):
            result.analysis_id.message_post(body=_('Result {} cancelled by {}. Reason: {}')
                                            .format(result.method_param_charac_id.tech_name, self.env.user.name,
                                                    self.reason))


class ResultReworkWizardLine(models.TransientModel):
    _name = 'result.cancel.wizard.line'
    _description = 'Cancel Result Line'

    wizard_id = fields.Many2one('result.cancel.wizard')
    result_id = fields.Many2one('lims.analysis.numeric.result')
    result_sel_id = fields.Many2one('lims.analysis.sel.result')
    result_compute_id = fields.Many2one('lims.analysis.compute.result')
    result_text_id = fields.Many2one('lims.analysis.text.result')
    name = fields.Char()
