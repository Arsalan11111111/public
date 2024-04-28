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
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        request_obj = request.env['lims.analysis.request'].sudo()
        request_count = request_obj.search_count(self.get_request_domain())

        analysis_obj = request.env['lims.analysis'].sudo()
        analysis_count = analysis_obj.search_count(self.get_analysis_domain())

        values.update({
            'request_count': request_count,
            'analysis_count': analysis_count,
        })
        return values

    def get_request_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'not in', ['cancel', 'draft'])
        ]
        return domain

    def get_analysis_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('rel_type', 'not in', ['cancel', 'draft'])
        ]
        return domain

    @http.route(['/my', '/my/home'])
    def home(self, **kw):
        res = super(CustomerPortal, self).home()
        if self._get_portal_rules('/my').get('portal_access'):
            return request.render('lims_web.portal_my_home_forbidden_access', res.qcontext)
        else:
            res.qcontext.update({
                'page_rules': {
                    'requests': self._get_page_rules('/my/requests'),
                    'analysis': self._get_page_rules('/my/analysis'),
                    'tours': self._get_page_rules('/my/tours'),
                }
            })
            return request.render(res.qcontext.get('response_template'), res.qcontext)
