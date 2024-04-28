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
from odoo import http
from odoo.http import request


class MailBrowser(http.Controller):

    @http.route('/mail/<int:id>/<token>', type='http', auth='public', website=True)
    def render_mail(self, token=None, id=None, **kw):
        try:
            domain = [
                ('id', '=', id),
                ('state', '=', 'done'),
                ('access_token', '=', token),
            ]
            mail = request.env['mailing.mailing'].sudo().search(domain)
            if mail:
                return request.render('mail_browser.render_mail_browser', {
                    'content': mail.body_html,
                })
            else:
                return request.not_found()
        except Exception:
            return request.not_found()
