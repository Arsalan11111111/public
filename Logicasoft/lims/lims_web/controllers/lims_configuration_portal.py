# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _get_rules(self, domain):
        res = {}
        for rule in request.env['lims.portal.configuration'].search(domain):
            res[rule.name] = rule.inactive
        return res

    def _get_portal_rules(self, url):
        return self._get_rules([('type', '=', 'portal'), '|', ('page', '=', url), ('page', '=', '')])

    def _get_page_rules(self, url):
        return self._get_rules([('type', '=', 'page'), ('page', '=', url), ('name', '=', url)])

    def _get_inactive_options(self, url):
        return [r['name'] for r in request.env['lims.portal.configuration'].search([
            ('type', '=', 'option'),
            ('page', '=', url),
            ('inactive', '=', True),
        ])]

    def _get_option_inactive_state(self, url, name, parent):
        return request.env['lims.portal.configuration'].search([
            ('type', '=', 'option'),
            ('page', '=', url),
            ('name', '=', name),
            ('parent', '=', parent),
        ], limit=1).inactive

    def _get_field_inactive_state(self, url, name):
        return request.env['lims.portal.configuration'].search([
            ('type', '=', 'field'),
            ('page', '=', url),
            ('name', '=', name),
        ], limit=1).inactive

    @http.route(['/my/lims_config_handler'], type='json', auth='user', website=True)
    def config_handler(self, data):
        name = data.get('name')
        type = data.get('type')
        page = data.get('page')
        parent = data.get('parent')
        lims_portal_config = request.env['lims.portal.configuration']
        domain = [('name', '=', name), ('type', '=', type), ('page', '=', page), ('parent', '=', parent)]
        res = lims_portal_config.search(domain)
        if res:
            res.write({'inactive': not res.inactive})
        else:
            lims_portal_config.create({'name': name, 'type': type, 'page': page, 'parent': parent})
        return True
