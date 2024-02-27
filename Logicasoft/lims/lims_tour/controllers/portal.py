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

from odoo import http, _, fields
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
from datetime import date, datetime, time


class PortalLims(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'tour_count' in counters:
            tour_count = request.env['lims.tour'].search_count(self._get_tour_domain()) \
                if request.env['lims.tour'].check_access_rights('read', raise_exception=False) else 0
            values['tour_count'] = tour_count
        return values

    # lims.analysis.requests
    def _tour_get_page_view_values(self, tour, access_token, **kwargs):
        values = {
            'page_name': 'tour',
            'tour_id': tour,
        }
        return self._get_page_view_values(tour, access_token, values, 'my_tours_history', False, **kwargs)

    def _get_tour_domain(self):
        return [('state', '!=', 'cancel')]

    def _get_tour_searchbar_sortings(self):
        return {
            't_name': {'label': _('Name'), 'order': 'name desc'},
            't_priority': {'label': _('Priority'), 'order': 'priority asc, date asc'},
            't_date': {'label': _('Date'), 'order': 'date desc'},
            't_state': {'label': _('Status'), 'order': 'state'},
            't_tour_name_id': {'label': _('Tour name'), 'order': 'tour_name_id'},
        }

    def _get_tour_defaut_sorting(self):
        return 't_name'

    def _get_tour_searchbar_filters(self):
        today_min = fields.Datetime.to_string(datetime.combine(date.today(), time.min))
        today_max = fields.Datetime.to_string(datetime.combine(date.today(), time.max))
        return {
            't10_all': {'label': _('All'), 'domain': []},
            't15_today': {'label': _('Today'),
                        'domain': [('date', '!=', False), ('date', '>=', today_min), ('date', '<', today_max)]},
            't20_plan': {'label': _('Plan'), 'domain': [('state', '=', 'plan')]},
            't21_todo': {'label': _('ToDo'), 'domain': [('state', '=', 'todo')]},
            't22_wip': {'label': _('WIP'), 'domain': [('state', '=', 'wip')]},
            't23_done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
        }

    def _get_tour_default_filter(self):
        return 't15_today'

    @http.route(['/my/tours', '/my/tours/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tours(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        LimsTour = request.env['lims.tour']

        domain = self._get_tour_domain()

        searchbar_sortings = self._get_tour_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = self._get_tour_defaut_sorting()
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_tour_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = self._get_tour_default_filter()
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        tour_count = LimsTour.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tours",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=tour_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        tours = LimsTour.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tours_history'] = tours.ids[:100]

        values.update({
            'date': date_begin,
            'tours': tours,
            'page_name': 'tour',
            'pager': pager,
            'default_url': '/my/tours',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("lims_tour.portal_my_tours", values)

    @http.route(['/my/tours/<int:tour_id>'], type='http', auth="public", website=True)
    def portal_my_tour_detail(self, tour_id, access_token=None, report_type=None, download=False, **kw):
        tour_sudo = self.portal_my_tour_detail_access(tour_id, access_token)
        values = self._tour_get_page_view_values(tour_sudo, access_token, **kw)
        return request.render("lims_tour.portal_tour_page", values)

    def portal_my_tour_detail_access(self, tour_id, access_token):
        try:
            tour_sudo = self._document_check_access('lims.tour', tour_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return tour_sudo
