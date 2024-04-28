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
from odoo.http import request


class PortalLims(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'request_count' in counters:
            request_count = request.env['lims.analysis.request'].search_count(self._get_request_domain()) \
                if request.env['lims.analysis.request'].check_access_rights('read', raise_exception=False) else 0
            values['request_count'] = request_count
        if 'analysis_count' in counters:
            analysis_count = request.env['lims.analysis'].search_count(self._get_analysis_domain()) \
                if request.env['lims.analysis'].check_access_rights('read', raise_exception=False) else 0
            values['analysis_count'] = analysis_count
        return values

    # lims.analysis.requests
    def _request_get_page_view_values(self, request, access_token, **kwargs):
        values = {
            'page_name': 'request',
            'request_id': request,
        }
        return self._get_page_view_values(request, access_token, values, 'my_requests_history', False, **kwargs)

    def _get_request_domain(self):
        return [('state', 'not in', ['draft', 'cancel'])]

    def _get_request_searchbar_sortings(self):
        return {
            'r_request_date': {'label': _('Date'), 'order': 'request_date desc'},
            'r_order_date': {'label': _('Order date'), 'order': 'order_date desc'},
            'r_date_plan': {'label': _('Plan date'), 'order': 'date_plan desc'},
            'r_name': {'label': _('Name'), 'order': 'name desc'},
            'r_state': {'label': _('Status'), 'order': 'state'},
        }

    def _get_request_defaut_sorting(self):
        return 'r_name'

    def _get_request_searchbar_filters(self):
        return {
            'r_all': {'label': _('All'), 'domain': []},
            'r_Accepted': {'label': _('Accepted'), 'domain': [('state', '=',  'accepted')]},
            'r_WIP': {'label': _('WIP'), 'domain': [('state', '=',  'in_progress')]},
            'r_Done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
        }

    def _get_request_default_filter(self):
        return 'r_all'

    def _get_request_searchbar_inputs(self):
        return {
                'all': {'label': _('Search in All'), 'input': 'all'},
                'name': {'label': _('Search in Name'), 'input': 'name'},
                'description': {'label': _('Search in description'), 'input': 'description'},
                'comment': {'label': _('Search in comment'), 'input': 'comment'},
                'reference': {'label': _('Search in reference'), 'input': 'reference'},
                'state': {'label': _('Search in state'), 'input': 'state'},
                }
    def _get_request_search_domain(self, search_in, search, model=None, search_domain=None):
        search_domain = search_domain or []
        if search_in in ('all', 'name'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('all', 'description'):
            search_domain.append([('description', 'ilike', search)])
        if search_in in ('all', 'comment'):
            search_domain.append([('comment', 'ilike', search)])
        if search_in in ('all', 'reference'):
            search_domain.extend(
                ([('customer_ref', 'ilike', search)],
                 [('customer_order_ref', 'ilike', search)],
                ))
        if search_in == 'state':
            lang = request.context.get('lang', 'en_US')
            if model._name and lang:
                states = model.with_context(lang=lang).get_request_state()
                search_domain.extend(
                    [('state', '=', state[0])]
                    for state in states
                    if search.upper() in state[1].upper()
                )
        return OR(search_domain)

    @http.route(['/my/requests', '/my/requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                           search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        lims_request = request.env['lims.analysis.request']

        domain = self._get_request_domain()

        searchbar_sortings = self._get_request_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = self._get_request_defaut_sorting()
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_request_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = self._get_request_default_filter()
        domain += searchbar_filters[filterby]['domain']
        searchbar_inputs = self._get_request_searchbar_inputs()

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        if search and search_in:
            domain += self._get_request_search_domain(search_in, search, lims_request)
        lims_request_sudo = lims_request.sudo()
        domain = AND([domain, request.env['ir.rule']._compute_domain(lims_request_sudo._name, 'read')])

        # count for pager
        request_count = lims_request.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/requests",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        requests = lims_request.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_requests_history'] = requests.ids[:100]

        values.update({
            'date': date_begin,
            'requests': requests,
            'page_name': 'request',
            'pager': pager,
            'default_url': '/my/requests',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("lims_base.portal_my_requests", values)

    @http.route(['/my/requests/<int:request_id>'], type='http', auth="public", website=True)
    def portal_my_request_detail(self, request_id, access_token=None, report_type=None, download=False, **kw):
        request_sudo = self.portal_my_request_detail_access(request_id, access_token)
        values = self._request_get_page_view_values(request_sudo, access_token, **kw)
        return request.render("lims_base.portal_request_page", values)

    def portal_my_request_detail_access(self, request_id, access_token):
        try:
            request_sudo = self._document_check_access('lims.analysis.request', request_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request_sudo

    # lims.analysis
    def _analysis_get_page_view_values(self, analysis, access_token, **kwargs):
        values = {
            'page_name': 'analysis',
            'analysis_id': analysis,
        }
        return self._get_page_view_values(analysis, access_token, values, 'my_analyses_history', False, **kwargs)

    def _get_analysis_domain(self):
        return [('rel_type', 'not in', ['draft', 'cancel'])]

    def _get_analysis_searchbar_sortings(self):
        return {
            'a_name': {'label': _('Name'), 'order': 'name desc'},
            'a_date_sample': {'label': _('Dates sample'), 'order': 'date_sample desc'},
            'a_date_plan': {'label': _('Plan date'), 'order': 'date_plan desc'},
            'a_state': {'label': _('Status'), 'order': 'state'},
            'a_rel_type': {'label': _('Stage'), 'order': 'stage_id'},
        }

    def _get_analysis_defaut_sorting(self):
        return 'a_name'

    def _get_analysis_searchbar_filters(self):
        return {
            'a00_all': {'label': _('All'), 'domain': []},
            'a10_plan': {'label': _('Plan'), 'domain': [('rel_type', '=', 'plan')]},
            'a11_todo': {'label': _('ToDo'), 'domain': [('rel_type', '=', 'todo')]},
            'a12_wip': {'label': _('WIP'), 'domain': [('rel_type', '=', 'wip')]},
            'a13_done': {'label': _('Done'), 'domain': [('rel_type', '=', 'done')]},
            'a14_validated1': {'label': _('Validated'), 'domain': [('rel_type', '=', 'validated1')]},
            'a15_validated2': {'label': _('Second Validation'), 'domain': [('rel_type', '=', 'validated2')]},
            'a20_conform': {'label': _('Conform'), 'domain': [('state', '=', 'conform')]},
            'a21_not_conform': {'label': _('Not conform'), 'domain': [('state', '=', 'not_conform')]},
        }

    def _get_analysis_default_filter(self):
        return 'a00_all'

    def _get_analysis_searchbar_inputs(self):
        return {
                'all': {'label': _('Search in All'), 'input': 'all'},
                'name': {'label': _('Search in Name'), 'input': 'name'},
                'description': {'label': _('Search in description'), 'input': 'description'},
                'comment': {'label': _('Search in comment'), 'input': 'comment'},
                'reference': {'label': _('Search in reference'), 'input': 'reference'},
                'state': {'label': _('Search in state'), 'input': 'state'},
                'stage': {'label': _('Search in stage'), 'input': 'stage'},
                }

    def _get_analysis_search_domain(self, search_in, search, model=None, search_domain=None):
        search_domain = search_domain or []
        if search_in in ('all', 'name'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('all', 'description'):
            search_domain.append([('description', 'ilike', search)])
        if search_in in ('all', 'comment'):
            search_domain.append([('comment', 'ilike', search)])
        if search_in in ('all', 'reference'):
            search_domain.append([('customer_ref', 'ilike', search)])
        if search_in == 'state':
            lang = request.context.get('lang', 'en_US')
            if model._name and lang:
                states = model.with_context(lang=lang).get_selection_state()
                search_domain.extend(
                    [('state', '=', state[0])]
                    for state in states
                    if search.upper() in state[1].upper()
                )
        if search_in == 'stage':
            search_domain.append([('stage_id', 'ilike', search)])
        return OR(search_domain)

    @http.route(['/my/analyses', '/my/analyses/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_analyses(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                           search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        lims_analysis = request.env['lims.analysis']

        domain = self._get_analysis_domain()

        searchbar_sortings = self._get_analysis_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = self._get_analysis_defaut_sorting()
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_analysis_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = self._get_analysis_default_filter()
        domain += searchbar_filters[filterby]['domain']
        searchbar_inputs = self._get_analysis_searchbar_inputs()

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        if search and search_in:
            domain += self._get_analysis_search_domain(search_in, search, lims_analysis)
        lims_analysis_sudo = lims_analysis.sudo()
        domain = AND([domain, request.env['ir.rule']._compute_domain(lims_analysis_sudo._name, 'read')])

        # count for pager
        analysis_count = lims_analysis.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/analyses",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'search_in': search_in, 'search': search},
            total=analysis_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        analyses = lims_analysis.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_analyses_history'] = analyses.ids[:100]

        values.update({
            'date': date_begin,
            'analyses': analyses,
            'page_name': 'analysis',
            'pager': pager,
            'default_url': '/my/analyses',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("lims_base.portal_my_analyses", values)

    @http.route(['/my/analyses/<int:analysis_id>'], type='http', auth="public", website=True)
    def portal_my_analysis_detail(self, analysis_id, access_token=None, report_type=None, download=False, **kw):
        analysis_sudo = self.portal_my_analysis_detail_access(analysis_id, access_token)
        values = self._analysis_get_page_view_values(analysis_sudo, access_token, **kw)
        return request.render("lims_base.portal_analysis_page", values)

    def portal_my_analysis_detail_access(self, analysis_id, access_token):
        try:
            analysis_sudo = self._document_check_access('lims.analysis', analysis_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return analysis_sudo
