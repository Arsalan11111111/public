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


class DoSopIsNullWizard(models.TransientModel):
    _name = 'do.sop.is.null.wizard'
    _description = 'Do test Is Null'

    @api.model
    def default_get(self, fields_list):
        """
        Generate line_ids from context.active_ids
        :param fields_list:
        :return:
        """
        res = super(DoSopIsNullWizard, self).default_get(fields_list)
        sop = self.env['lims.sop'].browse(self.env.context.get('active_id'))
        res.update({
            'line_ids': [(0, 0, {
                'analysis_result_id': result_id.id,
                'parameter_id': result_id.method_param_charac_id.id
            }) for result_id in sop.result_num_ids.filtered(lambda r: r.rel_type == 'wip')],
        })
        return res

    line_ids = fields.One2many('do.sop.is.null.wizard.line', 'wizard_id')
    is_null = fields.Boolean()

    @api.onchange('is_null')
    def onchange_is_null(self):
        self.line_ids.update({'is_null': self.is_null})

    def do_confirm(self):
        self.line_ids.filtered(lambda l: l.is_null).mapped('analysis_result_id').write({'is_null': True})
        return True


class DoSopIsNullWizardLine(models.TransientModel):
    _name = 'do.sop.is.null.wizard.line'
    _description = 'Do test Is Null Line'

    wizard_id = fields.Many2one('do.sop.is.null.wizard')
    analysis_result_id = fields.Many2one('lims.analysis.numeric.result')
    parameter_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter')
    is_null = fields.Boolean()
