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
from odoo import fields, models, api, _


class LimsAnalysisSelResult(models.Model):
    _name = 'lims.analysis.sel.result'
    _description = 'Analysis Selection Result'
    _inherit = ['lims.analysis.result']

    rel_sample_name = fields.Char('Sample Name', related='analysis_id.sample_name',
                                  help="The sample name of the analysis.")
    value_id = fields.Many2one('lims.result.value', 'Value (list)', index=True, ondelete='restrict')
    value_ids = fields.Many2many(related='method_param_charac_id.parameter_id.result_value_ids', compute_sudo=True)
    result_log_ids = fields.One2many('lims.result.log', 'sel_result_id', readonly=1)
    result_reason_id = fields.Many2one('lims.result.reason', 'Reason', copy=False)
    rel_parameter_id = fields.Many2one(related='method_param_charac_id.parameter_id', compute_sudo=True,
                                       string='characteristic Parameter')

    def write(self, vals):
        """
        Write the record, if value_id is in vals pass the result in done and check the state of the analysis
        :param vals:
        :return:
        """
        if 'value_id' in vals and not self.env.su:
            self.check_department()
        for record in self:
            if 'value_id' in vals:
                log = _('Old value: {} | New value: {}').format((record.value_id.name or '') if record.state else '-',
                                                                self.env['lims.result.value'].browse(
                                                                    vals.get('value_id')).name or '')
                result_log = record.prepare_result_log(log)
                self.env['lims.result.log'].create(result_log)
                if record.value_id:
                    vals.update({'change': True})
        if vals.get('result_reason_id'):
            vals.update({'change': True})
        res = super(LimsAnalysisSelResult, self).write(vals)
        if vals.get('value_id'):
            self.write({'user_id': self.env.user.id, 'date_result': fields.Datetime.now()})
            self.do_done()
        return res

    def do_cancel(self, cancel_stage_id=False):
        """
        Pass the result in stage "cancel", check if SOp could pass in done, check analysis state
        :return:
        """
        super(LimsAnalysisSelResult, self).do_cancel(cancel_stage_id=cancel_stage_id)
        for record in self:
            log = _('Result is cancelled')
            self.env['lims.result.log'].create({
                'sel_result_id': record.id,
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
        res = super(LimsAnalysisSelResult, self).do_rework(rework_reason, rework_stage_id=rework_stage_id)
        for record in self:
            log = _('Result is reworked')
            self.env['lims.result.log'].create({
                'sel_result_id': record.id,
                'user_id': self.env.uid,
                'log': log,
                'date': fields.Datetime.now()
            })
        return res

    def get_vals_rework(self):
        vals = super(LimsAnalysisSelResult, self).get_vals_rework()
        vals.update({
            'value_id': None,
        })
        return vals

    def check_result_conformity(self):
        """
        Set the state of the value in the result
        :return:
        """
        for record in self.filtered(lambda r: r.value_id and r.value_id.state):
            record._check_result_conformity()

    def _check_result_conformity(self):
        for record in self:
            record.state = record.value_id.state

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
            'context': {'default_analysis_sel_result_ids': self.ids},
            'target': 'new',
        }

    def open_cancel(self):
        return {
            'name': 'Cancel result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.cancel.wizard',
            'context': {'default_result_sel_ids': self.ids},
            'target': 'new',
        }

    def open_rework(self):
        return {
            'name': 'Rework result',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'result.rework.wizard',
            'context': {'default_result_sel_ids': self.ids},
            'target': 'new',
        }

    @api.onchange('value_id')
    def onchange_value_id(self):
        for record in self:
            if record.value_id:
                record.comment = record.value_id.message

    def get_result_value(self, default_str='', options=False, lang=False):
        """
        Default function to get interpreted value for a type of result (str)
        :param default_str: if the function returns an empty value, return this string instead
        :return:
        """
        if self.value_id:
            return self.value_id.name
        return default_str

    def prepare_result_log(self, log, result_reason_id=False):
        res = super().prepare_result_log(log, result_reason_id)
        res.update({
            'sel_result_id': self.id,
        })
        return res

    def get_result_uom(self):
        """
        Normalised function for qweb.
        :return:
        """
        return self.uom_id
