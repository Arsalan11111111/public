# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_notification_recipients(self, message, recipients):
        res = super(MailThread, self)._message_notification_recipients(message, recipients)
        if self.env.context.get('force_partner_ids'):
            for email_type, recipient_template_values in res.items():
                for follower in recipient_template_values['followers']:
                    if follower.id not in self.env.context.get('force_partner_ids', []):
                        recipient_template_values['followers'] = recipient_template_values['followers'] - follower
                for follower in recipient_template_values['not_followers']:
                    if follower.id not in self.env.context.get('force_partner_ids', []):
                        recipient_template_values['not_followers'] = recipient_template_values[
                                                                         'not_followers'] - follower
        return res
