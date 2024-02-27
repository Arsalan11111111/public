# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 LogicaSoft SPRL (<http://www.logicasoft.eu>).
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
{
    'name': 'Show Message Recipients',
    'version': '15.0.0.1',
    'category': 'Social Network',
    'depends': ['mail'],
    'author': 'LogicaSoft SPRL',
    'license': 'AGPL-3',
    'website': 'http://www.logicasoft.eu',
    'description': """
Based on Bista module, this module improves the sending message tools to automatically saw followers into the compose 
message wizard and allow the user to select only some followers to receive the mail.
""",
    'images': [],
    'demo': [],
    'data': [
        'wizards/mail_compose_message.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/mail_see_recipients/static/src/js/mail_chatter.js',
        ]
    },
    'installable': True,
    'application': False
}
