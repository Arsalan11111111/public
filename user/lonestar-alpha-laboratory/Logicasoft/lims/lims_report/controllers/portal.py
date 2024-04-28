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

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR, AND
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request, content_disposition
import base64


class PortalLims(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'report_count' in counters:
            report_count = request.env['lims.analysis.report'].search_count(self._get_report_domain()) \
                if request.env['lims.analysis.report'].check_access_rights('read', raise_exception=False) else 0
            values['report_count'] = report_count
        return values

    # lims.analysis.report
    def _report_get_page_view_values(self, report, access_token, **kwargs):
        values = {
            'page_name': 'report',
            'report_id': report,
        }
        return self._get_page_view_values(report, access_token, values, 'my_reports_history', False, **kwargs)

    def _get_report_domain(self):
        return [('state', '=', 'sent'), ('kanban_state', '!=', 'blocked')]

    def _get_report_searchbar_sortings(self):
        return {
            'r_name': {'label': _('Name'), 'order': 'name desc'},
            'r_date': {'label': _('Date'), 'order': 'date_sent desc'},
            'r_state': {'label': _('Status'), 'order': 'state'},
        }

    def _get_report_defaut_sorting(self):
        return 'r_name'

    def _get_report_searchbar_filters(self):
        return {
            'r10_all': {'label': _('All'), 'domain': []},
        }

    def _get_report_default_filter(self):
        return 'r10_all'

    def _get_report_searchbar_inputs(self):
        return {
                'all': {'label': _('Search in All'), 'input': 'all'},
                'name': {'label': _('Search in Name'), 'input': 'name'},
                'title': {'label': _('Search in Title'), 'input': 'title'},
                'comment': {'label': _('Search in comment'), 'input': 'comment'},
                'reference': {'label': _('Search in Reference'), 'input': 'reference'},
                'stage': {'label': _('Search in stage'), 'input': 'stage'},
                }

    def _get_report_search_domain(self, search_in, search, model=None, search_domain=None):
        search_domain = search_domain or []
        if search_in in ('all', 'name'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('all', 'title'):
            search_domain.append([('title', 'ilike', search)])
        if search_in in ('all', 'comment'):
            search_domain.append([('comment', 'ilike', search)])
        if search_in in ('all', 'reference'):
            search_domain.append([('customer_ref', 'ilike', search)])
        if search_in in ('stage'):
            lang = request.context.get('lang', 'en_US')
            if model._name and lang:
                states = model.with_context(lang=lang).get_state_selection()
                search_domain.extend(
                    [('state', '=', state[0])]
                    for state in states
                    if search.upper() in state[1].upper()
                )
        return OR(search_domain)

    @http.route(['/my/reports', '/my/reports/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_reports(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                           search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        lims_report = request.env['lims.analysis.report']

        domain = self._get_report_domain()

        searchbar_sortings = self._get_report_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = self._get_report_defaut_sorting()
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_report_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = self._get_report_default_filter()
        domain += searchbar_filters[filterby]['domain']
        searchbar_inputs = self._get_report_searchbar_inputs()

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        if search and search_in:
            domain += self._get_report_search_domain(search_in, search, lims_report)
        lims_report_sudo = lims_report.sudo()
        domain = AND([domain, request.env['ir.rule']._compute_domain(lims_report_sudo._name, 'read')])

        # count for pager
        report_count = lims_report.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/reports",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=report_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        reports = lims_report.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_reports_history'] = reports.ids[:100]

        values.update({
            'date': date_begin,
            'reports': reports,
            'page_name': 'report',
            'pager': pager,
            'default_url': '/my/reports',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("lims_report.portal_my_reports", values)

    @http.route(['/my/reports/<int:report_id>'], type='http', auth="public", website=True)
    def portal_my_report_detail(self, report_id, access_token=None, report_type=None, download=False, **kw):
        report_sudo = self.portal_my_report_detail_access(report_id, access_token)
        if report_type in ('html', 'pdf', 'text'):
            if report_sudo.state == 'sent' and report_sudo.kanban_state != 'blocked' and report_sudo.message_main_attachment_id:
                my_filecontent = base64.b64decode(report_sudo.message_main_attachment_id.datas or '')
                my_pdfhttpheaders = [('Content-Type', 'application/octet-stream'),
                                     ('Content-Disposition',
                                      content_disposition(report_sudo.message_main_attachment_id.display_name))]
                return http.request.make_response(my_filecontent, headers=my_pdfhttpheaders)
            else:
                return self._show_report(model=report_sudo, report_type=report_type,
                                         report_ref=report_sudo.report_id.xml_id, download=download)
        values = self._report_get_page_view_values(report_sudo, access_token, **kw)
        return request.render("lims_report.portal_report_page", values)

    def portal_my_report_detail_access(self, report_id, access_token):
        try:
            report_sudo = self._document_check_access('lims.analysis.report', report_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return report_sudo

    def _get_request_searchbar_filters(self):
        res = super()._get_request_searchbar_filters()
        res['r_Done'] = {'label': _('Done'), 'domain': [('state', 'in', ('done', 'report'))]}
        return res

    def _get_analysis_searchbar_filters(self):
        res = super()._get_analysis_searchbar_filters()
        res['a15_validated2'] = {'label': _('Second Validation'),
                                 'domain': [('rel_type', '=', 'validated2'), ('is_locked', '=', False)]}
        res['a16_validated2'] = {'label': _('Report'),
                                 'domain': [('rel_type', '=', 'validated2'), ('is_locked', '=', True)]}
        return res
