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
from odoo import models, fields, _, api, exceptions


class LimsAnalysisTextResult(models.Model):
    _name = 'lims.analysis.text.result'
    _description = 'Analysis text result'
    _inherit = ['lims.analysis.result']

    value = fields.Char(translate=True, copy=False)
    result_log_ids = fields.One2many('lims.result.log', 'text_result_id', readonly=1)
    result_reason_id = fields.Many2one('lims.result.reason', 'Reason', copy=False)

    def get_state_result_text(self):
        return [('conform', 'Conform'), ('not_conform', 'Not Conform'), ('unconclusive', 'Inconclusive')]

    def write(self, vals):
        if 'value' in vals and not self.env.su:
            self.check_department()
        for record in self:
            if 'value' in vals or 'state' in vals:
                log = _('Old value: {} | New value: {} || State: {} -> {}').format(
                    (record.value or '') if record.change else '-',
                    vals.get('value') or '',
                    (record.state or '') if record.change else '-',
                    vals.get('state') or '')
                result_log = record.prepare_result_log(log,
                                                       vals.get('result_reason_id') or record.result_reason_id.id)
                self.env['lims.result.log'].create(result_log)
                if record.value:
                    vals.update({'change': True})
        if vals.get('result_reason_id'):
            vals.update({'change': True})
        res = super(LimsAnalysisTextResult, self).write(vals)
        if vals.get('value'):
            self.write({'user_id': self.env.user.id, 'date_result': fields.Datetime.now()})
            self.do_done()
        return res

    def do_cancel(self, cancel_stage_id=False):
        """
        Pass the result in stage "cancel", check if SOp could pass in done, check analysis state
        :return:
        """
        super(LimsAnalysisTextResult, self).do_cancel(cancel_stage_id=cancel_stage_id)
        for record in self:
            log = _('Result is cancelled')
            self.env['lims.result.log'].create({
                'text_result_id': record.id,
                'user_id': self.env.uid,
                'log': log,
                'date': fields.Datetime.now()
            })
            record.change = True

    def do_rework(self, rework_reason='', rework_stage_id=False):
        """
        Pass the result in stage "rework", copy the result, set the sop in stage todo
        :return:
        """
        res = super(LimsAnalysisTextResult, self).do_rework(rework_reason, rework_stage_id=rework_stage_id)
        for record in self:
            log = _('Result is reworked')
            self.env['lims.result.log'].create({
                'text_result_id': record.id,
                'user_id': self.env.uid,
                'log': log,
                'date': fields.Datetime.now()
            })
        return res

    def get_vals_rework(self):
        vals = super(LimsAnalysisTextResult, self).get_vals_rework()
        vals.update({
            'value': None,
        })
        return vals

    def open_wizard_mass_change_result(self):
        """
        Open the wizard for mass change on result
        :return:
        """
        return {
            'name': 'Mass Change Result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mass.change.result.wizard',
            'context': {'default_analysis_text_result_ids': self.ids},
            'target': 'new',
        }

    def open_cancel(self):
        return {
            'name': 'Cancel result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.cancel.wizard',
            'context': {'default_result_text_ids': self.ids},
            'target': 'new',
        }

    def open_rework(self):
        return {
            'name': 'Rework result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.rework.wizard',
            'context': {'default_result_text_ids': self.ids},
            'target': 'new',
        }

    def get_result_value(self, default_str='', options=False, lang=False):
        """
        Default function to get interpreted value for a type of result (str)
        :param default_str: if the function returns an empty value, return this string instead
        :return:
        """
        if self.value:
            return self.value
        return default_str
