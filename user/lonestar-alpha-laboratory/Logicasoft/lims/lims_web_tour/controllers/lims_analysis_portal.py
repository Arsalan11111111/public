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
from odoo.addons.lims_web.controllers.lims_analysis_portal import CustomerPortal
from odoo import http, _
from odoo.http import request

ALLOWED_FIELDS = [
    {'field': 'location_id', 'type': 'int'},
    {'field': 'address', 'type': 'char'},
]


class CustomerPortal(CustomerPortal):

    @http.route(['/my/analysis', '/my/analysis/page/<int:page>'])
    def portal_my_analysis(self, **kw):
        res = super(CustomerPortal, self).portal_my_analysis(**kw)
        default_url = res.qcontext['default_url']
        res.qcontext['searchbar_sortings'].update({
            'sampling_point_id': {'label': _('Sampling Point'), 'order': 'sampling_point_id %o', 'inactive': self._get_field_inactive_state(default_url, 'sampling_point_id')},
        })
        res.qcontext['searchbar_inputs'].update({
            'sampling_point_id': {'input': 'sampling_point_id', 'label': _('Sampling Point'), 'sortable': True, 'inactive': self._get_field_inactive_state(default_url, 'name')},
        })
        res.qcontext['searchby_sortby_fields'].update({
            'sampling_point_id': {'input': 'sampling_point_id', 'label': _('Sampling Point'), 'inactive': self._get_field_inactive_state(default_url, 'date_report')},
        })
        return res

    def analysis_get_page_view_values(self, analysis_id, access_token, **kwargs):
        values = super(CustomerPortal, self).analysis_get_page_view_values(analysis_id, access_token, **kwargs)
        values['location_ids'] = request.env['lims.sampling.point.location'].sudo().search([])
        values['tour'] = analysis_id.tour_id
        return values

    @http.route(['/my/analysis/update/<int:analysis_id>'], type='http', auth="public", website=True)
    def update_analysis(self, analysis_id, access_token=None, **kw):
        res = super(CustomerPortal, self).update_analysis(analysis_id, access_token, **kw)
        vals = {}
        analysis_obj = request.env['lims.analysis'].sudo()
        for arg in kw:
            if kw.get(arg):
                type, id, field = arg.split('/')
                if type == 'analysis':
                    record = next((r for r in ALLOWED_FIELDS if r.get('field') == field), None)
                    if record:
                        vals.update({field: int(kw.get(arg)) if record.get('type') == 'int' else kw.get(arg)})
        analysis = analysis_obj.browse(analysis_id)
        if vals:
            analysis.write(vals)
        return res
