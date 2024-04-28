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
{
    'name': 'Mail Message Subtype Variable',
    'version': '14.0.0.1',
    'category': 'Others',
    'description': """
    Mail Message Subtype Variable, is a module that let you introduce customized descriptions to your mails using
     variables referencing your record. It is as simple as calling your record with the alias 'o'.
      For exemple you can call the record name with the following {o.name}
    """,
    'author': 'LogicaSoft SPRL',
    'depends': ['mail'],
    'license': 'LGPL-3',
    'data': [],
    'css': [],
    'test': [],
    'installable': False,
}
