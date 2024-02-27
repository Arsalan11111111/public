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


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    description = fields.Text('Description', translate=True, help='Description that will be added in the message posted'
                                                                  ' for this subtype. If void, the name will be added '
                                                                  'instead.You can use fields and function from '
                                                                  'current object by using {o.something}. For example '
                                                                  'if you want to display the name of your object, just'
                                                                  ' add {o.name} in this field')
