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


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        if self.env.context.get('force_notify_only_partners'):
            partner_ids = [el[-1] for el in values.get('partner_ids', [])]
            return super(MailMessage, self.with_context(force_partner_ids=partner_ids)).create(values)
        return super(MailMessage, self).create(values)
