# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2018 LogicaSoft SPRL (<http://www.logicasoft.eu>).
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
from odoo import models, fields, api, exceptions, _


class MailRemover(models.TransientModel):
    _name = 'mail.remover'
    _description = 'Mail Remover'

    message = fields.Html(string='Message', readonly=True)
    author_id = fields.Many2one(comodel_name='res.partner', string='Author', readonly=True)
    subject = fields.Char(string='Subject', readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        Get the message to delete and update the wizard's value.
        :param fields_list: List of the fields which the default value will be returned
        :return: The wizard's values updated
        """
        res = super(MailRemover, self).default_get(fields_list)
        mail_message = self.env['mail.message'].browse(self.env.context['default_message_id']).ensure_one()
        res.update({'message': mail_message.body,
                    'author_id': mail_message.author_id.id,
                    'subject': mail_message.subject})
        return res

    @api.multi
    def confirm(self):
        """
        Check if the user can delete e-mail if he is not the author (group id = lgk_mail_organizer.lgk_mail_organizer_remover)
        Then, execute the unlink
        :return:
        """
        group = self.env.ref('mail_organizer.mail_organizer_remover')
        if self._uid in [user.id for user in group.users]:
            self.env['mail.message'].browse(self.env.context['default_message_id']).unlink()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        else:
            raise exceptions.Warning(_('You don\'t have the permission to delete a message.'))
