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
from odoo import models, fields, api, exceptions
from odoo.tools.safe_eval import safe_eval
import re


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        '''
        we fetch for the record to evaluate, we catch all the strings in between {} and try to evaluate them
        if no exception is raised we update the body else we pass
        :param values:
        :return:
        '''
        model = values.get('model')
        res_id = values.get('res_id')
        body = values.get('body')
        if model and res_id and body:
            body = self.replace_body(body, model, res_id)
            values.update(body=body)
        return super(MailMessage, self).create(values)

    @api.multi
    def message_format(self):
        res = super(MailMessage, self).message_format()
        for message in res:
            subtype_description = message.get('subtype_description')
            model = message.get('model')
            res_id = message.get('res_id')
            if subtype_description and model and res_id:
                message.update({
                    'subtype_description': self.replace_body(subtype_description, model, res_id)
                })
        return res

    def replace_body(self, message, model, res_id):
        o = self.env[model].browse(res_id)
        for variable_to_evaluate in re.findall(r"\{([^}]+)\}", message):
            try:
                value = safe_eval(variable_to_evaluate, {'o': o})
                message = message.replace('{%s}' % variable_to_evaluate, str(value))
            except:
                pass
        return message
