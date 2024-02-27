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
from odoo import _, api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    """
    Override default_get method to set default value for partner_ids and subject of mail
    """
    @api.model
    def default_get(self, fields):
        result = super(MailComposeMessage, self).default_get(fields)
        partner_list = []
        if self._context.get('default_model'):
            # updated default value for model
            result['model'] = str(self._context.get('default_model'))
        if self._context.get('sub'):
            # updated default value for subject
            result['subject'] = str(self._context.get('sub'))
        if self._context.get('partner_ids'):
            partners = self._context.get('partner_ids')
            for partner in partners:
                p_id = partner.get('res_id')
                partner_list.append(p_id)
            # updated default value for partner_ids
            result['partner_ids'] = [(6, 0, partner_list)]
        return result

    def send_mail(self, auto_commit=False):
        return super(MailComposeMessage, self.with_context(force_notify_only_partners=True)).send_mail(
            auto_commit=auto_commit)
