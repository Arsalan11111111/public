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


class SopReworkWizard(models.TransientModel):
    _name = 'sop.rework.wizard'
    _description = 'Rework test'

    sop_id = fields.Many2one('lims.sop', 'Test')
    line_ids = fields.One2many('sop.rework.wizard.line', 'wizard_id')
    reason = fields.Char(string="Reason", required=True)
    check_all = fields.Boolean(string="Check all")

    @api.onchange('sop_id')
    def create_line_ids(self):
        sop = self.sop_id
        line_ids = line_obj = self.env['sop.rework.wizard.line']

        for result in sop.result_num_ids.filtered(lambda r: r.rel_type in ['done', 'validated']):
            line_ids += line_obj.new({'result_id': result.id, 'name': result.method_param_charac_id.tech_name})
        for result_sel in sop.result_sel_ids.filtered(lambda r: r.rel_type in ['done', 'validated']):
            line_ids += line_obj.new({'result_sel_id': result_sel.id, 'name': result_sel.method_param_charac_id.tech_name})
        for result_text in sop.result_text_ids.filtered(lambda r: r.rel_type in ['done', 'validated']):
            line_ids += line_obj.new({
                'result_text_id': result_text.id,
                'name': result_text.method_param_charac_id.tech_name,
            })
        self.line_ids = line_ids

    def confirm_rework(self):
        self.sop_id.message_post(body='Reason to rework : '+self.reason)
        for line_id in self.line_ids.filtered(lambda line: line.is_checked):
            if line_id.result_id:
                line_id.result_id.do_rework(rework_reason=self.reason)
            elif line_id.result_sel_id:
                line_id.result_sel_id.do_rework(rework_reason=self.reason)
            elif line_id.result_text_id:
                line_id.result_text_id.do_rework(rework_reason=self.reason)

    @api.onchange('check_all')
    def check_all_is_checked(self):
        for line_id in self.line_ids:
            line_id.is_checked = self.check_all


class SopReworkWizardLine(models.TransientModel):
    _name = 'sop.rework.wizard.line'
    _description = 'Rework test Line'

    wizard_id = fields.Many2one('sop.rework.wizard')
    result_id = fields.Many2one('lims.analysis.numeric.result')
    result_sel_id = fields.Many2one('lims.analysis.sel.result')
    result_text_id = fields.Many2one('lims.analysis.text.result')
    name = fields.Char()
    is_checked = fields.Boolean()
