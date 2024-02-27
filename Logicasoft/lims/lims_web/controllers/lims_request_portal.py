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
import datetime
import logging
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools import consteq
from collections import OrderedDict
from odoo.osv.expression import OR
from odoo.addons.web.controllers.main import content_disposition

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/requests', '/my/requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='name',
                           filterbystage=None, order_type='asc', **kw):
        values = self._prepare_portal_layout_values()
        request_obj = request.env['lims.analysis.request'].sudo()
        default_url = '/my/requests'

        domain = self.get_request_domain()

        searchbar_sortings = {
            'date': {'label': _('Create Date'), 'order': 'create_date %o', 'inactive': self._get_field_inactive_state(default_url, 'date')},
            'name': {'label': _('N°'), 'order': 'name %o', 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'customer_order_ref': {'label': _('Reference'), 'order': 'customer_order_ref %o', 'inactive': self._get_field_inactive_state(default_url, 'customer_order_ref')},
            'customer_ref': {'label': _('Client Reference'), 'order': 'customer_ref %o', 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'request_date': {'label': _('Request Date'), 'order': 'request_date %o', 'inactive': self._get_field_inactive_state(default_url, 'request_date')},
            'date_plan': {'label': _('Date Plan'), 'order': 'date_plan %o', 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_report': {'label': _('Date Report'), 'order': 'date_report %o', 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
            'state': {'label': _('State'), 'order': 'state %o', 'inactive': self._get_field_inactive_state(default_url, 'state')},
        }
        searchbar_filters_stages = {
            'all': {'name': 'all', 'field': 'state', 'label': _('All'), 'domain': [], 'inactive': self._get_option_inactive_state(default_url, 'all', 'state')},
            'draft': {'name': 'draft', 'field': 'state', 'label': _('Draft'), 'domain': [('state', '=', 'draft')], 'inactive': self._get_option_inactive_state(default_url, 'draft', 'state')},
            'accepted': {'name': 'accepted', 'field': 'state', 'label': _('Accepted'), 'domain': [('state', '=', 'accepted')], 'inactive': self._get_option_inactive_state(default_url, 'accepted', 'state')},
            'in_progress': {'name': 'in_progress', 'field': 'state', 'label': _('In Progress'), 'domain': [('state', '=', 'in_progress')], 'inactive': self._get_option_inactive_state(default_url, 'in_progress', 'state')},
            'done': {'name': 'done', 'field': 'state', 'label': _('Done'), 'domain': [('state', '=', 'done')], 'inactive': self._get_option_inactive_state(default_url, 'done', 'state')},
            'report': {'name': 'report', 'field': 'state', 'label': _('Report'), 'domain': [('state', '=', 'report')], 'inactive': self._get_option_inactive_state(default_url, 'report', 'state')},
            'cancelled': {'name': 'cancelled', 'field': 'state', 'label': _('Cancelled'), 'domain': [('state', '=', 'cancelled')], 'inactive': self._get_option_inactive_state(default_url, 'cancelled', 'state')},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('N°'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'analysis_count': {'input': 'analysis_count', 'label': _('Analysis Count'), 'sortable': False, 'inactive': self._get_field_inactive_state(default_url, 'analysis_count')},
            'customer_order_ref': {'input': 'customer_order_ref', 'label': _('Reference'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'customer_order_ref')},
            'customer_ref': {'input': 'customer_ref', 'label': _('Client Reference'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'partner_id': {'input': 'partner_id', 'label': _('Customer'), 'sortable': False, 'inactive': self._get_field_inactive_state(default_url, 'partner_id')},
            'request_type_id': {'input': 'request_type_id', 'label': _('Request Type'), 'sortable': False, 'inactive': self._get_field_inactive_state(default_url, 'request_type_id')},
            'request_date': {'input': 'request_date', 'label': _('Request Date'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'request_date')},
            'date_plan': {'input': 'date_plan', 'label': _('Date Plan'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_report': {'input': 'date_report', 'label': _('Date Report'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
            'state': {'input': 'state', 'label': _('State'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'state')},
        }
        searchby_sortby_fields = {
            'name': {'input': 'name', 'label': _('N°'), 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'customer_order_ref': {'input': 'customer_order_ref', 'label': _('Reference'), 'inactive': self._get_field_inactive_state(default_url, 'customer_order_ref')},
            'customer_ref': {'input': 'customer_ref', 'label': _('Client Reference'), 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'partner_id': {'input': 'partner_id', 'label': _('Customer'), 'inactive': self._get_field_inactive_state(default_url, 'partner_id')},
            'request_type_id': {'input': 'request_type_id', 'label': _('Request Type'), 'inactive': self._get_field_inactive_state(default_url, 'request_type_id')},
            'request_date': {'input': 'request_date', 'label': _('Request Date'), 'inactive': self._get_field_inactive_state(default_url, 'request_date')},
            'date_plan': {'input': 'date_plan', 'label': _('Date Plan'), 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_report': {'input': 'date_report', 'label': _('Date Report'), 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
        }

        # default sort by order
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order'].replace('%o', order_type)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        if not filterbystage:
            filterbystage = 'all'
        domain += searchbar_filters_stages[filterbystage]['domain']

        if search and search_in:
            search_domain = []
            if search_in in ['request_date', 'date_plan', 'date_report']:
                try:
                    format_str = '%d/%m/%Y'
                    search = datetime.datetime.strptime(search, format_str).date()
                except ValueError as e:
                    _logger.warning(e)
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in == 'customer_order_ref':
                search_domain = OR([search_domain, [('customer_order_ref', 'ilike', search)]])
            if search_in == 'customer_ref':
                search_domain = OR([search_domain, [('customer_ref', 'ilike', search)]])
            if search_in == 'partner_id':
                search_domain = OR([search_domain, [('partner_id.name', 'ilike', search)]])
            if search_in == 'request_type_id':
                search_domain = OR([search_domain, [('request_type_id.name', 'ilike', search)]])
            if search_in == 'request_date':
                search_domain = OR([search_domain, [('request_date', 'ilike', search)]])
            if search_in == 'date_plan':
                search_domain = OR([search_domain, [('date_plan', 'ilike', search)]])
            if search_in == 'date_report':
                search_domain = OR([search_domain, [('date_report', '>=', search), ('date_report', '<=', search)]])
            domain += search_domain

        # adapts requests domain with inactive options
        domain += [('state', 'not in', self._get_inactive_options(default_url))]

        # count for pager
        request_count = request_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url=default_url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterbystage': filterbystage},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        requests = request_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'requests': requests,
            'page_name': 'requests',
            'pager': pager,
            'default_url': default_url,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters_stages': OrderedDict(sorted(searchbar_filters_stages.items())),
            'sortby': sortby,
            'filterbystage': filterbystage,
            'search_in': search_in,
            'searchby_sortby_fields': searchby_sortby_fields,
            'order_type': order_type,
            'portal_rules': self._get_portal_rules(default_url),
            'page_rules': self._get_page_rules(default_url),
        })
        return request.render("lims_web.portal_my_requests", values)

    @http.route(['/my/requests/<int:request_id>'], type='http', auth="public", website=True)
    def portal_my_request_detail(self, request_id, access_token=None, **kw):
        default_url = '/my/requests'
        try:
            reques_id_sudo = self.request_check_access(request_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = self.request_get_page_view_values(reques_id_sudo, access_token, **kw)
        values['report_ids'] = request.env['lims.analysis.report'].sudo().search([
            ('analysis_request_id', '=', int(values['request_id'].id)),
            ('state', 'in', ['validated', 'sent'])
        ])
        values['portal_rules'] = self._get_portal_rules(default_url)
        return request.render("lims_web.portal_request_page", values)

    def request_get_page_view_values(self, request_id, access_token, **kwargs):
        values = {
            'page_name': 'request',
            'request_id': request_id,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token

        return values

    def request_check_access(self, request_id, access_token=None):
        request_id = request.env['lims.analysis.request'].browse([request_id])
        request_id_sudo = request_id.sudo()
        try:
            request_id.check_access_rights('read')
            request_id.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(request_id_sudo.access_token, access_token):
                raise
        return request_id_sudo

    @http.route('/my/requests/download/<request_id>', type='http', auth="public", website=True)
    def download_report(self, request_id):
        report_ids = request.env['lims.analysis.report'].sudo().search([
            ('analysis_request_id', '=', int(request_id)),
            ('state', 'in', ['validated', 'sent'])
        ])
        if report_ids:
            report_id = report_ids.sorted(lambda r: r.create_date, reverse=True)[0]
            attachment = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'lims.analysis.report'),
                ('res_id', '=', report_id.id)
            ])
            if len(attachment) > 1:
                attachment = attachment.sorted(lambda r: r.create_date, reverse=True)[0]
            if attachment:
                filecontent = base64.b64decode(attachment.datas or '')
                pdfhttpheaders = [('Content-Type', 'application/octet-stream'),
                                  ('Content-Disposition', content_disposition(attachment.display_name))]
                return http.request.make_response(filecontent, headers=pdfhttpheaders)

    @http.route('/my/report/download/<report_id>', type='http', auth="public", website=True)
    def download_specific_report(self, report_id):
        report = request.env['lims.analysis.report'].sudo().browse(report_id)
        attachment = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', 'lims.analysis.report'),
            ('res_id', '=', report.id)
        ], limit=1)
        if attachment:
            filecontent = base64.b64decode(attachment.datas or '')
            pdfhttpheaders = [('Content-Type', 'application/octet-stream'),
                              ('Content-Disposition', content_disposition(attachment.display_name))]
            return http.request.make_response(filecontent, headers=pdfhttpheaders)
