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


class PrintQwebLabelWizard(models.TransientModel):
    _name = 'print.qweb.label.wizard'
    _description = 'Print Label'

    analysis_id = fields.Many2one('lims.analysis')
    line_ids = fields.One2many('print.qweb.label.wizard.lines', 'wizard_id')

    @api.onchange('analysis_id')
    def create_lines(self):
        line_obj = self.env['print.qweb.label.wizard.lines']
        analysis_ids = self.env['lims.analysis'].browse(self.env.context.get('active_ids'))
        if self.env.context.get('default_analysis_ids'):
            analysis_ids = self.env['lims.analysis'].browse(self.env.context.get('default_analysis_ids'))
        deactivate_container = self.env['ir.config_parameter'].sudo().get_param('deactivate_container_for_label', False)
        for sop_id in analysis_ids.mapped('sop_ids'):
            line_obj.new({
                'sop_id': sop_id.id,
                'wizard_id': self.id,
                'nb_print': sop_id.method_id.nb_label_total,
                'deactivate_container': deactivate_container,
            })

    def print_label(self):
        return self.env.ref('lims_base.sop_report_action').report_action(self.line_ids.sop_id)


class PrintQwebLabelWizardLines(models.TransientModel):
    _name = 'print.qweb.label.wizard.lines'
    _description = 'Print Label Line'

    wizard_id = fields.Many2one('print.qweb.label.wizard', ondelete='cascade')
    sop_id = fields.Many2one('lims.sop', 'Test')
    analysis_id = fields.Many2one('lims.analysis', related='sop_id.analysis_id')
    nb_print = fields.Integer('Number of prints')
    deactivate_container = fields.Boolean()
