# Copyright 2020 Subteno IT
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.tools import formataddr
import logging


_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _split_by_server(self):
        user_config = self.env['ir.config_parameter'].sudo().get_param('mail.split_server_mail_by_user')
        for mail in self.filtered(lambda r: not r.mail_server_id):
            user = self.env['res.users'].search([('partner_id', '=', mail.author_id.id)])
            if user_config == 'True':
                server_id = user.server_mail_id
                if not server_id:
                    alias_domain = user.company_id.sudo().force_alias_domain
                    server_id = self.env['ir.mail_server'].search([('force_alias_domain', '=', alias_domain)])

                partner = user.partner_id
                mail.mail_server_id = server_id
                mail.email_from = formataddr((partner.name, partner.email))
            else:
                alias_domain = self._get_alias_domain(mail, user)
                if alias_domain:
                    company_server_id = self.env['ir.mail_server'].search([('force_alias_domain', '=', alias_domain)])
                    sign_config = self.env['ir.config_parameter'].sudo().get_param('mail.use_different_signature')
                    user_alias = user.mail_user_alias_ids.filtered(lambda r: r.alias_domain == alias_domain)
                    if sign_config:
                        if user_alias and user_alias.signature_alias:
                            mail.body_html = mail.body_html.replace(user.signature, user_alias.signature_alias)

                    partner = user_alias or user.partner_id
                    mail.mail_server_id = company_server_id
                    mail.email_from = formataddr((partner.name, partner.email.split('@')[0] + '@' + alias_domain))
                    mail.reply_to = formataddr((partner.name, 'catchall' + '@' + alias_domain))

        return super(MailMail, self)._split_by_server()

    def _get_alias_domain(self, mail, user):
        alias_domain = ''
        if 'force_alias_domain' in self.env[mail.model]._fields.keys():
            alias_domain = self.env[mail.model].sudo().browse(mail.res_id).force_alias_domain
        if not alias_domain:
            alias_domain = self.env.company.sudo().force_alias_domain

        return alias_domain

