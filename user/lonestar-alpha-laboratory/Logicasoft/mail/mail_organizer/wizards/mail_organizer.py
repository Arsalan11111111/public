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
from odoo import fields, api, models, exceptions, _


class MailOrganizer(models.TransientModel):
    _name = 'mail.organizer'
    _description = 'Mail Organizer'

    @api.model
    def _select_models(self):
        """
        Get all objects which can be used with the mail organizer
        :return: List of tuples of the models
        """
        modules_ids = self.env['ir.model'].search([('mail_organizer', '=', True)])
        return [(m.model, m.name) for m in modules_ids]

    message_id = fields.Many2one('mail.message', string="Message")
    res = fields.Char('Resource', readonly=True)
    model = fields.Selection(_select_models, string="Model", readonly=True)
    new_model = fields.Reference(_select_models, string='New model')
    subject = fields.Char('Subject', readonly=True)
    email_from = fields.Char('Email')
    author_id = fields.Many2one('res.partner', string='Author', readonly=True)

    @api.model
    def default_get(self, fields_list):
        """
        Check if the model linked with the message can be used with the mail organizer.
        Then, get the resource and update the wizard's values.
        :param fields_list: List of the fields which the default value will be returned
        :return: The wizard's values updated or raise an exception
        """
        res = super(MailOrganizer, self).default_get(fields_list)
        message_to_assign_id = self.env.context['default_message_id']
        message_id = self.env['mail.message'].browse(message_to_assign_id)
        if any(x[0] == message_id.model for x in self._select_models()):
            if message_id.res_id:
                obj = self.env[message_id.model].browse(message_id.res_id)
                resource = getattr(obj, obj._rec_name)
            res.update({
                'model': message_id.model,
                'res': resource,
                'email_from': message_id.email_from,
                'author_id': (message_id.author_id and message_id.author_id.id or None),
                'subject': message_id.subject,
            })
            return res

        else:
            raise exceptions.Warning(_('Please add this object type in the mail organizer configuration'))

    def confirm(self):
        """
        Update the model and the resource id of the message then reload the page
        :return: Client action that reload the page
        """
        for record in self:
            data = {'model': record.new_model._inherit, 'res_id': record.new_model.id}
            record.message_id.write(data)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
