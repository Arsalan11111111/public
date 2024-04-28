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
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class PortalLims(CustomerPortal):

    def _get_analysis_searchbar_sortings(self):
        res = super()._get_analysis_searchbar_sortings()
        res['a30_sampling_point_id'] = {'label': _('Sampling Point'), 'order': 'sampling_point_id'}
        return res

    def _get_analysis_searchbar_filters(self):
        res = super()._get_analysis_searchbar_filters()
        res['a30_has_sampling_point_id'] = {'label': _('Sampling point is set'), 'domain': [('sampling_point_id', '!=', False)]}
        return res

    def _get_analysis_searchbar_inputs(self):
        res = super()._get_request_searchbar_inputs()
        res['sampling_point'] = {'label': _('Search in sampling point'), 'input': 'sampling_point'}
        return res

    def _get_analysis_search_domain(self, search_in, search, model=None, search_domain=None):
        search_domain = search_domain or []
        if search_in in ('all', 'sampling_point'):
            search_domain.append([('sampling_point_id', 'ilike', search)])
        return super()._get_request_search_domain(search_in, search, model=model, search_domain=search_domain)
