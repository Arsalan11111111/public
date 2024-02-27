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
import socket

from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        result = super(ResUsers, self).create(vals)
        system_name = socket.gethostname()
        template_id = self.env.ref('mail_new_user.template_mail_new_user')
        template_id.write({'subject': "Odoo New User : {0} [{1}]".format(result.name, system_name)})
        template_id.send_mail(result.id, force_send=True)
        return result

    @api.multi
    def toggle_active(self):
        super(ResUsers, self).toggle_active()
        system_name = socket.gethostname()
        template_id = self.env.ref('mail_new_user.template_mail_new_user')
        for record in self:
            if record.active:
                template_id.write({'subject': "Odoo activation User : {0} [{1}]".format(record.name, system_name)})
                template_id.send_mail(record.id, force_send=True)
