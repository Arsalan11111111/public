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
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools import consteq
from collections import OrderedDict
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    @http.route(['/my/tours', '/my/tours/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tours(self, page=1, date_begin=None, date_end=None, search=None, search_in='name', sortby=None,
                        filterbystage=None, order_type='asc', **kw):
        values = self._prepare_portal_layout_values()
        tour_obj = request.env['lims.tour'].sudo()
        default_url = '/my/tours'

        domain = self.get_tour_domain()

        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date %o', 'inactive': self._get_field_inactive_state(default_url, 'create_date')},
            'date': {'label': _('Date'), 'order': 'date %o', 'inactive': self._get_field_inactive_state(default_url, 'date')},
            'name': {'label': _('Name'), 'order': 'name %o', 'inactive': self._get_field_inactive_state(default_url, 'name')},
        }
        searchbar_filters_stages = {
            'all': {'name': 'all', 'field': 'state', 'label': _('All'), 'domain': [], 'inactive': self._get_option_inactive_state(default_url, 'all', 'state')},
            'plan': {'name': 'plan', 'field': 'state', 'label': _('Plan'), 'domain': [('state', '=', 'plan')], 'inactive': self._get_option_inactive_state(default_url, 'plan', 'state')},
            'todo': {'name': 'todo', 'field': 'state', 'label': _('To do'), 'domain': [('state', '=', 'todo')], 'inactive': self._get_option_inactive_state(default_url, 'todo', 'state')},
            'wip': {'name': 'wip', 'field': 'state', 'label': _('In Progress'), 'domain': [('state', '=', 'wip')], 'inactive': self._get_option_inactive_state(default_url, 'wip', 'state')},
            'done': {'name': 'done', 'field': 'state', 'label': _('Done'), 'domain': [('state', '=', 'done')], 'inactive': self._get_option_inactive_state(default_url, 'done', 'state')},
            'cancel': {'name': 'cancel', 'field': 'state', 'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')], 'inactive': self._get_option_inactive_state(default_url, 'cancel', 'state')},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Name'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'tour_name_id': {'input': 'tour_name_id', 'label': _('Tour Name'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'tour_name_id')},
            'date': {'input': 'date', 'label': _('Date'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date')},
            'sampler_team_id': {'input': 'sampler_team_id', 'label': _('Sampler Team'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'sampler_team_id')},
            'sampler_id': {'input': 'sampler_id', 'label': _('Sampler'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'sampler_id')},
            'state': {'input': 'state', 'label': _('Stage'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'state')},
            'analysis_ids': {'input': 'analysis_ids', 'label': _('Analysis'), 'sortable': True, 'inactive': True},
            'sampling_point_ids': {'input': 'sampling_point_ids', 'sortable': True, 'label': _('Sampling Point'), 'inactive': True},
            'sop_ids': {'input': 'sop_ids', 'label': _('SOP'), 'sortable': True, 'inactive': True},
        }
        searchby_sortby_fields = {
            'name': {'input': 'name', 'label': _('N°'), 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'tour_name_id': {'input': 'tour_name_id', 'label': _('Tour Name'), 'inactive': self._get_field_inactive_state(default_url, 'tour_name_id')},
            'date': {'input': 'date', 'label': _('Date'), 'inactive': self._get_field_inactive_state(default_url, 'date')},
            'sampler_team_id': {'input': 'sampler_team_id', 'label': _('Sampler Team'), 'inactive': self._get_field_inactive_state(default_url, 'sampler_team_id')},
            'sampler_id': {'input': 'sampler_id', 'label': _('Sampler'), 'inactive': self._get_field_inactive_state(default_url, 'sampler_id')},
            'state': {'input': 'state', 'label': _('Stage'), 'inactive': self._get_field_inactive_state(default_url, 'state')},
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
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in == 'tour_name_id':
                search_domain = OR([search_domain, [('tour_name_id.name', 'ilike', search)]])
            if search_in == 'sampler_team_id':
                search_domain = OR([search_domain, [('sampler_team_id.name', 'ilike', search)]])
            if search_in == 'sampler_id':
                search_domain = OR([search_domain, [('sampler_id.name', 'ilike', search)]])
            if search_in == 'analysis_ids':
                search_domain = OR([search_domain, [('tour_line_ids.analysis_id.name', 'ilike', search)]])
            if search_in == 'sampling_point_ids':
                search_domain = OR([search_domain, [('tour_line_ids.rel_sampling_point_id.name', 'ilike', search)]])
            if search_in == 'sop_ids':
                search_domain = OR([search_domain, [('tour_line_ids.analysis_id.sop_ids.name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        tour_count = tour_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url=default_url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterbystage': filterbystage},
            total=tour_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        tours = tour_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'tours': tours,
            'page_name': 'tours',
            'pager': pager,
            'default_url': default_url,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters_stages': OrderedDict(sorted(searchbar_filters_stages.items())),
            'searchbar_inputs': searchbar_inputs,
            'sortby': sortby,
            'filterbystage': filterbystage,
            'search_in': search_in,
            'searchby_sortby_fields': searchby_sortby_fields,
            'order_type': order_type,
            'portal_rules': self._get_portal_rules(default_url),
            'page_rules': self._get_page_rules(default_url),
        })
        return request.render("lims_web_tour.portal_my_tours", values)

    @http.route(['/my/tours/<int:tour_id>'], type='http', auth="public", website=True)
    def portal_my_tour_detail(self, tour_id, access_token=None, **kw):
        try:
            tour_sudo = self.tour_check_access(tour_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = self.tour_get_page_view_values(tour_sudo, access_token, **kw)
        return request.render("lims_web_tour.portal_tour_page", values)

    def tour_get_page_view_values(self, tour_id, access_token, **kwargs):
        values = {
            'page_name': 'tour',
            'tour': tour_id,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token

        return values

    @http.route(['/my/tours/update/<int:tour_id>'], type='http', auth="public", website=True)
    def update_tour(self, tour_id, access_token=None, **kw):
        return http.redirect_with_hash('/my/tours/{}'.format(tour_id))

    def tour_check_access(self, tour_id, access_token=None):
        tour_id = request.env['lims.tour'].browse([tour_id])
        tour_id_sudo = tour_id.sudo()
        try:
            tour_id.check_access_rights('read')
            tour_id.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(tour_id_sudo.access_token, access_token):
                raise
        return tour_id_sudo
