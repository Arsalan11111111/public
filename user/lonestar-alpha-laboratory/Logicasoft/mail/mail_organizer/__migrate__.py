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
{
    'name': 'LGK Mail Organizer',
    'version': '14.0.0.1',
    'category': 'Social Network',
    'depends': ['mail'],
    'author': 'LogicaSoft SPRL',
    'license': 'AGPL-3',
    'website': 'http://www.logicasoft.eu',
    'description': """
This module allows you to assign a message to a resource dynamically 
and to delete messages.

You can configure the available model 
through Settings > Technical > Email > Email Organizer
""",
    'images': [],
    'demo': [],
    'data': [
        'security/lgk_model_security.xml',
        'wizards/mail_organizer.xml',
        'wizards/mail_remover.xml',
        'static/static_load.xml',
        'views/model_view.xml',
        'views/mail_view.xml',
        'views/menu.xml'
    ],
    'qweb': ['static/src/xml/mail.xml'],
    'js': ['static/src/js/mail.js'],
    'css': ['static/src/css/mail.css'],
    'installable': False,
    'application': False
}
