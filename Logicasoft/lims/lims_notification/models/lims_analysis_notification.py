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
from odoo import fields, models, _, api
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging

_logger = logging.getLogger(__name__)


TYPE_OBJECT_MAPPING = {
    'lims.analysis.numeric.result': 'nu',
    'lims.analysis.compute.result': 'ca',
    'lims.analysis.sel.result': 'se',
    'lims.analysis.text.result': 'tx',
}


class LimsAnalysisNotification(models.Model):
    _name = 'lims.analysis.notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Analysis Notification'

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        return self.env['lims.laboratory'].search([('default_laboratory', '=', True)])

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    language_id = fields.Many2one('res.lang', required=True)
    partner_ids = fields.Many2many('res.partner', 'rel_to_partner_notification', 'notification_id', 'partner_id',
                                   string='To', required=True)
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', required=True, default=get_default_laboratory)
    analysis_stage_ids = fields.Many2many('lims.analysis.stage', string='Analysis Stage', required=True)
    matrix_ids = fields.Many2many('lims.matrix', string='Matrix')
    reason_ids = fields.Many2many('lims.analysis.reason', string='Analysis Reason')
    a_partner_ids = fields.Many2many('res.partner', 'rel_a_partner_notification', 'notification_id', 'partner_id',
                                     string='Partner')
    state = fields.Selection('get_state', 'Analysis State')
    result_stage_ids = fields.Many2many('lims.result.stage', string='Result Stage', required=True)
    result_state_ids = fields.Many2many('lims.analysis.notification.result.state', 'rel_notification_result_state',
                                        'notification_id', 'state_id', string='Result State')
    parameter_ids = fields.Many2many('lims.parameter', required=True)
    template_id = fields.Many2one('mail.template', 'Mail template',
                                  default=lambda self: self.env.ref('lims_notification.email_analysis_notification',
                                                                    raise_if_not_found=False))
    cron_id = fields.Many2one('ir.cron', 'Planned action',
                              domain=[('model_name', '=', 'lims.analysis.notification'), '|',
                                      ('active', '=', True), ('active', '=', False)],
                              default=lambda self:
                              self.env.ref('lims_notification.send_daily_mail_analysis_notification',
                                           raise_if_not_found=False))
    last_sent_date = fields.Datetime('Last sent date')
    send_if_empty = fields.Boolean('Send if empty')

    @api.model
    def get_state(self):
        return [
            ('init', _('Init')),
            ('conform', _('Conform')),
            ('not_conform', _('Not Conform')),
            ('unconclusive', _('Inconclusive'))
        ]

    @api.model
    def send_mail_analysis_notification(self):
        notification_ids = self or self.search([])
        for notification_id in notification_ids:
            mail_template = notification_id.template_id
            result_nu = notification_id.get_result('lims.analysis.numeric.result')
            result_ca = notification_id.get_result('lims.analysis.compute.result')
            result_sel = notification_id.get_result('lims.analysis.sel.result')
            result_tx = notification_id.get_result('lims.analysis.text.result')
            if result_nu or result_ca or result_sel or result_tx or notification_id.send_if_empty:
                template_fields = ['subject', 'email_from', 'body_html', 'email_cc', 'email_to', 'partner_to', 'reply_to',
                                   'scheduled_date']
                template_values = mail_template.generate_email(notification_id.id, template_fields)
                template_values.update({
                    'mail_auto_delete': mail_template.auto_delete,
                    'partner_ids': notification_id.partner_ids.ids,
                    'message_type': 'comment',
                    'subtype_id': self.env.ref('mail.mt_note').id,
                    'body': template_values['body_html'],
                })
                template_values.pop('res_id')
                template_values.pop('model')
                notification_id.message_post(**template_values)
                notification_id.last_sent_date = fields.Datetime.now()
                result_vals = {
                    'date_notification_sent': fields.Datetime.now()
                }
                result_nu.update(result_vals)
                result_ca.update(result_vals)
                result_tx.update(result_vals)
                result_sel.update(result_vals)

    def get_domain_analysis(self):
        domain = [('laboratory_id', '=', self.laboratory_id.id)]
        if self.matrix_ids:
            domain.append(('matrix_id', 'in', self.matrix_ids.ids))
        if self.reason_ids:
            domain.append(('reason_id', 'in', self.reason_ids.ids))
        if self.a_partner_ids:
            domain.append(('partner_id', 'in', self.a_partner_ids.ids))
        if self.state:
            domain.append(('state', '=', self.state))
        if self.analysis_stage_ids:
            domain.append(('stage_id', 'in', self.analysis_stage_ids.ids))
        return domain

    def get_analysis(self, domain):
        return self.env['lims.analysis'].search(domain)

    def get_domain_result(self, format_parameter):
        domain = self.get_domain_analysis()
        analysis_ids = self.get_analysis(domain)
        parameter = self.parameter_ids.filtered(lambda p: p.format == format_parameter)
        method_param_charac_ids = parameter.method_param_charac_ids
        domain = [('analysis_id', 'in', analysis_ids.ids),
                  ('method_param_charac_id', 'in', method_param_charac_ids.ids),
                  ('stage_id', 'in', self.result_stage_ids.ids), '|',
                  ('date_notification_sent', '>', self.last_sent_date),
                  ('date_notification_sent', '=', False)
                  ]
        if self.result_state_ids:
            domain.append(('state', 'in', self.result_state_ids.mapped('state')))
        return domain

    def get_result(self, model):
        """
        Get all results that must be sent to notification mail
        :param model: one of the 4 models of result
        :return: the result of the search
        """
        format_parameter = TYPE_OBJECT_MAPPING.get(model)
        if not format_parameter:
            return False
        domain = self.get_domain_result(format_parameter)
        result_ids = self.env[model].search(domain)
        return result_ids

    def get_all_vals(self):
        result_nu_ids = self.get_result('lims.analysis.numeric.result')
        result_se_ids = self.get_result('lims.analysis.sel.result')
        result_ca_ids = self.get_result('lims.analysis.compute.result')
        result_tx_ids = self.get_result('lims.analysis.text.result')
        dict_result_value = []
        dict_result_value += self.get_result_vals(result_nu_ids)
        dict_result_value += self.get_result_vals(result_se_ids)
        dict_result_value += self.get_result_vals(result_ca_ids)
        dict_result_value += self.get_result_vals(result_tx_ids)
        return dict_result_value

    def get_result_vals(self, result_ids):
        dict_result_value = []
        for result_id in result_ids:
            dict_result_value.append(result_id.get_notification_vals())
        return dict_result_value
