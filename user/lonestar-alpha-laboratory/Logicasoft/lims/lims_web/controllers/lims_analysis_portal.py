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
import logging
import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import http, _, fields
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools import consteq
from collections import OrderedDict
from odoo.osv.expression import OR

FLOAT_FIELDS = ['value', 'dilution_factor']
INT_FIELDS = ['value_id']
CHAR_FIELDS = ['comment', 'note', 'value']

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/analysis', '/my/analysis/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_analysis(self, page=1, date_begin=None, date_end=None, search=None, search_in='name', sortby=None,
                           filterbystage=None, order_type='asc', **kw):
        values = self._prepare_portal_layout_values()
        analysis_obj = request.env['lims.analysis'].sudo()
        default_url = '/my/analysis'

        domain = self.get_analysis_domain()
        if kw.get('filterbyrequestid') and kw.get('filterbyrequestid').isdigit():
            domain += [('request_id', '=', int(kw.get('filterbyrequestid')))]

        searchbar_sortings = {
            'date': {'label': _('Create Date'), 'order': 'create_date %o', 'inactive': self._get_field_inactive_state(default_url, 'date')},
            'name': {'label': _('N°'), 'order': 'name %o', 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'request_id': {'label': _('Request'), 'order': 'request_id %o', 'inactive': self._get_field_inactive_state(default_url, 'request_id')},
            'partner_id': {'label': _('Customer'), 'order': 'partner_id %o', 'inactive': self._get_field_inactive_state(default_url, 'partner_id')},
            'date_plan': {'label': _('Date Plan'), 'order': 'date_plan %o', 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_sample': {'label': _('Date Sample'), 'order': 'date_sample %o', 'inactive': self._get_field_inactive_state(default_url, 'date_sample')},
            'partner_contact_ids': {'label': _('Customer Contact'), 'order': 'partner_contact_ids %o', 'inactive': self._get_field_inactive_state(default_url, 'partner_contact_ids')},
            'customer_ref': {'label': _('Client Reference'), 'order': 'customer_ref %o', 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'date_report': {'label': _('Date Report'), 'order': 'date_report %o', 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
            'laboratory_id': {'label': _('Laboratory'), 'order': 'laboratory_id %o', 'inactive': self._get_field_inactive_state(default_url, 'laboratory_id')},
            'matrix_id': {'label': _('Matrix'), 'order': 'matrix_id %o', 'inactive': self._get_field_inactive_state(default_url, 'matrix_id')},
            'stage_id': {'label': _('Stage'), 'order': 'stage_id %o', 'inactive': self._get_field_inactive_state(default_url, 'stage_id')},
            'state': {'label': _('State'), 'order': 'state %o', 'inactive': self._get_field_inactive_state(default_url, 'state')},
            # adding pre-support for lims_web_tour
            'sampling_point_id': {'label': _('Sampling Point'), 'order': 'sampling_point_id %o', 'inactive': True},
        }
        searchbar_filters_stages = {
            'all': {'name': 'all', 'field': 'stage_id', 'label': _('All'), 'domain': [], 'inactive': self._get_option_inactive_state(default_url, 'all', 'stage_id')},
            'draft': {'name': 'draft', 'field': 'stage_id', 'label': _('Draft'), 'domain': [('stage_id', '=', 1)], 'inactive': self._get_option_inactive_state(default_url, 'draft', 'stage_id')},
            'plan': {'name': 'plan', 'field': 'stage_id', 'label': _('Plan'), 'domain': [('stage_id', '=', 2)], 'inactive': self._get_option_inactive_state(default_url, 'plan', 'stage_id')},
            'received': {'name': 'received', 'field': 'stage_id', 'label': _('Received'), 'domain': [('stage_id', '=', 3)], 'inactive': self._get_option_inactive_state(default_url, 'received', 'stage_id')},
            'wip': {'name': 'wip', 'field': 'stage_id', 'label': _('In Progress'), 'domain': [('stage_id', '=', 4)], 'inactive': self._get_option_inactive_state(default_url, 'wip', 'stage_id')},
            'done': {'name': 'done', 'field': 'stage_id', 'label': _('Done'), 'domain': [('stage_id', '=', 5)], 'inactive': self._get_option_inactive_state(default_url, 'done', 'stage_id')},
            'validated1': {'name': 'validated1', 'field': 'stage_id', 'label': _('Validated'), 'domain': [('stage_id', '=', 6)], 'inactive': self._get_option_inactive_state(default_url, 'validated1', 'stage_id')},
            'validated2': {'name': 'validated2', 'field': 'stage_id', 'label': _('Second Validation'), 'domain': [('stage_id', '=', 7)], 'inactive': self._get_option_inactive_state(default_url, 'validated2', 'stage_id')},
            'cancel': {'name': 'cancel', 'field': 'stage_id', 'label': _('Cancel'), 'domain': [('stage_id', '=', 8)], 'inactive': self._get_option_inactive_state(default_url, 'cancel', 'stage_id')},
        }
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('N°'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'request_id': {'input': 'request_id', 'label': _('Request'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'request_id')},
            'partner_id': {'input': 'partner_id', 'label': _('Customer'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'partner_id')},
            'partner_contact_ids': {'input': 'partner_contact_ids', 'label': _('Customer Contact'), 'sortable': False, 'inactive': self._get_field_inactive_state(default_url, 'partner_contact_ids')},
            'customer_ref': {'input': 'customer_ref', 'label': _('Client Reference'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'date_plan': {'input': 'date_plan', 'label': _('Date Plan'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_sample': {'input': 'date_sample', 'label': _('Date Sample'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date_sample')},
            'date_report': {'input': 'date_report', 'label': _('Date Report'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
            'laboratory_id': {'input': 'laboratory_id', 'label': _('Laboratory'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'laboratory_id')},
            'matrix_id': {'input': 'matrix_id', 'label': _('Matrix'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'matrix_id')},
            'stage_id': {'input': 'stage_id', 'label': _('Stage'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'stage_id')},
            'state': {'input': 'state', 'label': _('State'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'state')},
        }
        searchby_sortby_fields = {
            'name': {'input': 'name', 'label': _('N°'), 'inactive': self._get_field_inactive_state(default_url, 'name')},
            'request_id': {'input': 'request_id', 'label': _('Request'), 'inactive': self._get_field_inactive_state(default_url, 'request_id')},
            'partner_id': {'input': 'partner_id', 'label': _('Customer'), 'inactive': self._get_field_inactive_state(default_url, 'partner_id')},
            'date_plan': {'input': 'date_plan', 'label': _('Date Plan'), 'inactive': self._get_field_inactive_state(default_url, 'date_plan')},
            'date_sample': {'input': 'date_sample', 'label': _('Date Sample'), 'inactive': self._get_field_inactive_state(default_url, 'date_sample')},
            'partner_contact_ids': {'input': 'partner_contact_ids', 'label': _('Customer Contact'), 'inactive': self._get_field_inactive_state(default_url, 'partner_contact_ids')},
            'customer_ref': {'input': 'customer_ref', 'label': _('Client Reference'), 'inactive': self._get_field_inactive_state(default_url, 'customer_ref')},
            'date_report': {'input': 'date_report', 'label': _('Date Report'), 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
            'laboratory_id': {'input': 'laboratory_id', 'label': _('Laboratory'), 'inactive': self._get_field_inactive_state(default_url, 'laboratory_id')},
            'matrix_id': {'input': 'matrix_id', 'label': _('Matrix'), 'inactive': self._get_field_inactive_state(default_url, 'matrix_id')},
            'stage_id': {'input': 'stage_id', 'label': _('Stage'), 'inactive': self._get_field_inactive_state(default_url, 'stage_id')},
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
            if search_in in ['date_plan', 'date_sample', 'date_report']:
                try:
                    format_str = '%d/%m/%Y'
                    search = datetime.datetime.strptime(search, format_str).date()
                except ValueError as e:
                    _logger.warning(e)
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in == 'request_id':
                search_domain = OR([search_domain, [('request_id.name', 'ilike', search)]])
            if search_in == 'partner_id':
                search_domain = OR([search_domain, [('partner_id.name', 'ilike', search)]])
            if search_in == 'partner_contact_ids':
                search_domain = OR([search_domain, [('partner_contact_ids.name', 'ilike', search)]])
            if search_in == 'customer_ref':
                search_domain = OR([search_domain, [('customer_ref', 'ilike', search)]])
            if search_in == 'date_plan':
                search_domain = OR([search_domain, [('date_plan', '>=', search), ('date_plan', '<=', search)]])
            if search_in == 'date_sample':
                search_domain = OR([search_domain, [('date_sample', '>=', search), ('date_sample', '<=', search)]])
            if search_in == 'date_report':
                search_domain = OR([search_domain, [('date_report', '>=', search), ('date_report', '<=', search)]])
            if search_in == 'laboratory_id':
                search_domain = OR([search_domain, [('laboratory_id.name', 'ilike', search)]])
            if search_in == 'matrix_id':
                search_domain = OR([search_domain, [('matrix_id.name', 'ilike', search)]])
            if search_in == 'stage_id':
                search_domain = OR([search_domain, [('stage_id.name', 'ilike', search)]])
            # adding possibility support for lims_web_tour
            if search_in == 'sampling_point_id':
                search_domain = OR([search_domain, [('sampling_point_id.name', 'ilike', search)]])
            domain += search_domain

        # adapts analysis domain with inactive options
        domain += [('stage_id.type', 'not in', self._get_inactive_options(default_url))]

        # count for pager
        analysis_count = analysis_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url=default_url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterbystage': filterbystage},
            total=analysis_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        analysis = analysis_obj.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'analysis': analysis,
            'page_name': 'analysis',
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
            'is_intern_user': request.env.user.has_group('base.group_user'),
            'ids_with_downloadable_reports': [record.id for record in analysis if request.env['lims.analysis.report'].sudo().search([
                ('analysis_request_id', '=', int(record.request_id)),
                ('state', 'in', ['validated', 'sent'])
            ], order='id')]
        })
        return request.render("lims_web.portal_my_analysis", values)

    @http.route(['/my/analysis/<int:analysis_id>'], type='http', auth="public", website=True)
    def portal_my_analysis_detail(self, analysis_id, access_token=None, **kw):
        User = request.env.user
        try:
            analysis_sudo = self.analysis_check_access(analysis_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = self.analysis_get_page_view_values(analysis_sudo, access_token, **kw)
        values['portal_rules'] = self._get_portal_rules('/my/analysis')
        values['is_manager'] = User.has_group('lims_tour.lims_tour_manager')
        values['is_user'] = User.has_group('lims_tour.lims_tour_user')
        values['is_client'] = User.partner_id in analysis_sudo.partner_id.child_ids
        return request.render("lims_web.portal_analysis_page", values)

    def analysis_get_page_view_values(self, analysis_id, access_token, **kwargs):
        has_reworkable_results_web = request.env['ir.config_parameter'].sudo().get_param(
            'has_reworkable_results_web'
        )
        is_result_value = analysis_id.result_num_ids.filtered(
            lambda r: r.method_param_charac_id.is_published_portal and (
                    (has_reworkable_results_web or not (r.value or r.is_null)) and r.rel_type != 'cancel'))
        is_result_sel = analysis_id.result_sel_ids.filtered(
            lambda r: r.method_param_charac_id.is_published_portal and (
                    (has_reworkable_results_web or not (r.value_id or r.is_null)) and r.rel_type != 'cancel'))
        is_result_text = analysis_id.result_text_ids.filtered(
            lambda r: r.method_param_charac_id.is_published_portal and (
                    (has_reworkable_results_web or not (r.value or r.is_null)) and r.rel_type != 'cancel'))
        is_result_compute = analysis_id.result_compute_ids.filtered(
            lambda r: r.method_param_charac_id.is_published_portal and (
                    (has_reworkable_results_web or not (r.value or r.is_null)) and r.rel_type != 'cancel'))
        values = {
            'page_name': 'analysis_id',
            'analysis_id': analysis_id,
            'is_result_value': is_result_value and True or False,
            'is_result_sel': is_result_sel and True or False,
            'is_result_text': is_result_text and True or False,
            'is_result_compute': is_result_compute and True or False,
            'result_value': is_result_value,
            'result_sel': is_result_sel,
            'result_text': is_result_text,
            'result_compute': is_result_compute,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token
        return values

    def analysis_check_access(self, analysis_id, access_token=None):
        analysis_id = request.env['lims.analysis'].browse([analysis_id])
        analysis_id_sudo = analysis_id.sudo()
        try:
            analysis_id.check_access_rights('read')
            analysis_id.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(analysis_id_sudo.access_token, access_token):
                raise
        return analysis_id_sudo

    @http.route(['/my/analysis/update/<int:analysis_id>'], type='http', auth="public", website=True)
    def update_analysis(self, analysis_id, access_token=None, **kw):
        result_list = {}
        sel_result_list = {}
        text_result_list = {}
        vals = {}
        result_obj = request.env['lims.analysis.numeric.result']
        sel_result_obj = request.env['lims.analysis.sel.result']
        text_result_obj = request.env['lims.analysis.text.result']
        analysis_obj = request.env['lims.analysis']
        for arg in kw:
            if kw.get(arg):
                type, id, field = arg.split('/')
                if type == 'result':
                    if id not in result_list.keys():
                        result_list[id] = {'date_start': fields.Datetime.now()}
                    if field in FLOAT_FIELDS:
                        result_list[id][field] = float(kw.get(arg))
                        if field == 'value' and float(kw.get(arg)) == 0.0:
                            result_list[id]['is_null'] = True
                    elif field in INT_FIELDS:
                        result_list[id][field] = int(kw.get(arg))
                    elif field in CHAR_FIELDS:
                        result_list[id][field] = kw.get(arg)
                elif type == 'result_sel':
                    if id not in sel_result_list.keys():
                        sel_result_list[id] = {'date_start': fields.Datetime.now()}
                    if field in INT_FIELDS:
                        sel_result_list[id][field] = int(kw.get(arg))
                    elif field in CHAR_FIELDS:
                        sel_result_list[id][field] = kw.get(arg)
                elif type == 'result_text':
                    if id not in text_result_list.keys():
                        text_result_list[id] = {'date_start': fields.Datetime.now()}
                    if field in INT_FIELDS:
                        text_result_list[id][field] = int(kw.get(arg))
                    elif field in CHAR_FIELDS:
                        text_result_list[id][field] = kw.get(arg)
                elif type == 'analysis':
                    if field in INT_FIELDS:
                        vals.update({field: int(kw.get(arg))})
                    elif field in CHAR_FIELDS:
                        vals.update({field: kw.get(arg)})
        for result in result_list:
            result_id = result_obj.browse(int(result))
            result_id.write(result_list.get(result))
        for sel_result in sel_result_list:
            result_id = sel_result_obj.browse(int(sel_result))
            result_id.write(sel_result_list.get(sel_result))
        for text_result in text_result_list:
            result_id = text_result_obj.browse(int(text_result))
            result_id.write(text_result_list.get(text_result))
        analysis = analysis_obj.browse(analysis_id)
        if (result_list or sel_result_list or text_result_list) and not analysis.date_sample:
            vals['date_sample'] = fields.Datetime.now()
        if (result_list or sel_result_list or text_result_list) and not analysis.sampler_id and \
                request.env.user.employee_ids:
            vals['sampler_id'] = request.env.user.employee_ids[0].id
        if vals:
            analysis.write(vals)
        return request.redirect('/my/analysis/{}'.format(analysis_id))

    @http.route(['/my/analysis/cancel_result/<int:analysis_id>/<int:method_param_charac_id>'], type='http', auth="public", website=True)
    def cancel_result(self, analysis_id, method_param_charac_id, access_token=None, **kw):
        result = request.env['lims.analysis.numeric.result'].search([
            ('analysis_id', '=', analysis_id), ('method_param_charac_id', '=', method_param_charac_id)])
        if not result:
            result = request.env['lims.analysis.sel.result'].search([('analysis_id', '=', analysis_id),
                                                                     ('method_param_charac_id', '=', method_param_charac_id)])
        if not result:
            result = request.env['lims.analysis.text.result'] \
                .search([('analysis_id', '=', analysis_id), ('method_param_charac_id', '=', method_param_charac_id)])
        values = {
            'result': result
        }
        return request.render("lims_web.portal_cancel_result", values)

    @http.route(['/my/analysis/cancel/result/<int:analysis_id>/<int:method_param_charac_id>'], type='http', auth="public", website=True)
    def confirm_cancel_result(self, analysis_id, method_param_charac_id, access_token=None, **kw):
        result = request.env['lims.analysis.numeric.result'].search(
            [('analysis_id', '=', analysis_id), ('method_param_charac_id', '=', method_param_charac_id)])
        if not result:
            result = request.env['lims.analysis.sel.result'].search([('analysis_id', '=', analysis_id),
                                                                     ('method_param_charac_id', '=', method_param_charac_id)])
        if not result:
            result = request.env['lims.analysis.text.result'] \
                .search([('analysis_id', '=', analysis_id), ('method_param_charac_id', '=', method_param_charac_id)])
        result.do_cancel()
        result.analysis_id.message_post(body=_('Result {} cancelled reason: {} by {}')
                                        .format(result.method_param_charac_id.tech_name, kw.get('cancel_reason'), request.env.user.name))
        return request.redirect('/my/analysis/{}'.format(analysis_id))

    @http.route(['/my/analysis/rework_result'], type='json', auth='public', website=True)
    def confirm_rework_result(self, analysis_id, method_param_charac_id, reason, model):
        result = request.env[model].search([
            ('analysis_id', '=', analysis_id),
            ('method_param_charac_id', '=', method_param_charac_id),
        ])
        return result.do_rework(rework_reason=str(reason))
