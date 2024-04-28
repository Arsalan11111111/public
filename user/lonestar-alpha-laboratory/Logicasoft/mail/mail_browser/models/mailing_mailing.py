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
import random
import string
from odoo import models, fields, api, _


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    access_token = fields.Char('Security Token', copy=False)

    def _get_view_in_browser_template(self, id, token):
        text = _('[View this e-mail online]')
        return '''
            <nav class="navbar navbar-expand-lg navbar-light bg-light"
                style=" padding-top: 5px;
                    background-color: rgb(234, 236, 237);
                    text-align: center;">
                <div class="collapse navbar-collapse">
                    <a href="/mail/%i/%t" class="navbar-text"
                        style="color: rgb(121, 121, 121);">%s</a>
                </div>
            </nav>
        '''.replace('%i', str(id)).replace('%t', token).replace('%s', text)

    @api.model
    def create(self, vals):
        res = super(MailingMailing, self).create(vals)
        chars = string.ascii_lowercase + string.digits
        token = ''.join(random.choice(chars) for i in range(64))
        res.update({
            'access_token': token,
            'body_html': self._get_view_in_browser_template(
                res.id, token) + res['body_html'],
        })
        return res

    @api.onchange('body_html')
    def _onchange_body_html(self):
        '''
        This onchange prevents to remove the 'View in browser' template.
        This was especially occuring when the write function is triggered.
        Directly overriding the write function seemed not to be a great
        idea in this particular case.
        '''
        body_html = self.body_html and not self.body_html[:4] == '<nav'
        if body_html and self._origin.id and self.access_token:
            self.body_html = self._get_view_in_browser_template(
                self._origin.id, self.access_token) + self.body_html
