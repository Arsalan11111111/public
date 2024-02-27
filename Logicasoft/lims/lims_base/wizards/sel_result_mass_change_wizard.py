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
from odoo import models, fields, api, exceptions, _


class SelResultMassChangeWizard(models.TransientModel):
    _name = 'sel.result.mass.change.wizard'
    _description = 'Mass change of selection results'

    @api.model
    def default_get(self, fields_list):
        res = super(SelResultMassChangeWizard, self).default_get(fields_list)
        sel_result_ids = self.env['lims.analysis.sel.result'].browse(self.env.context.get('active_ids'))
        parameter_ids = sel_result_ids.mapped('method_param_charac_id').mapped('parameter_id')

        result_value_ids = self.env['lims.result.value'].search([])
        for parameter_id in parameter_ids:
            result_value_ids &= parameter_id.mapped('result_value_ids')

        if not result_value_ids:
            raise exceptions.UserError(_("This operation can not be done on results "
                                         "without at least one common result value"))

        res.update({
            'result_value_ids': result_value_ids.ids,
            'line_ids': [(0, 0, {'sel_result_id': sel_result_id.id}) for sel_result_id in sel_result_ids],
        })
        return res

    line_ids = fields.One2many('sel.result.mass.change.wizard.line', 'wizard_id')
    result_value_ids = fields.Many2many('lims.result.value', string='Selection result value')
    value_id = fields.Many2one('lims.result.value', 'Value', domain="[('id', 'in', result_value_ids)]")

    @api.onchange('value_id')
    def onchange_value_id(self):
        self.line_ids.update({
            'value_id': self.value_id.id
        })

    def do_confirm(self):
        for line_id in self.line_ids:
            line_id.sel_result_id.write({
                'value_id': line_id.value_id.id
            })


class SelResultMassChangeWizardLine(models.TransientModel):
    _name = 'sel.result.mass.change.wizard.line'
    _description = 'Line for mass change of selection results'

    wizard_id = fields.Many2one('sel.result.mass.change.wizard')
    sel_result_id = fields.Many2one('lims.analysis.sel.result', 'Result')
    rel_parameter_char_id = fields.Many2one('lims.method.parameter.characteristic',
                                            related='sel_result_id.method_param_charac_id')
    rel_analysis_id = fields.Many2one('lims.analysis', related='sel_result_id.analysis_id')
    rel_sop_id = fields.Many2one('lims.sop', related='sel_result_id.sop_id')
    value_id = fields.Many2one('lims.result.value', 'Value')
