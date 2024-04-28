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
from odoo.addons.lims_base.controllers.parameters_helper import ParametersHelper
from odoo import http
from odoo.http import request


class ParametersHelper(ParametersHelper):

    def _get_pack_info(self, base_obj):
        res = super()._get_pack_info(base_obj)
        res['is_additional_invoiced'] = base_obj.get_is_additional_invoiced()
        return res

    @http.route()
    def create_results(self, results):
        datas = results.get('lims_datas')
        invoiced_pack_ids = False
        if datas:
            invoiced_pack_ids = datas.get('invoiced_pack') and request.env['lims.parameter.pack'].browse(
                datas.get('invoiced_pack'))
        split_packs = False
        element_id = super().create_results(results)
        if 'pack_of_pack_invoiced_ids' in element_id._fields and invoiced_pack_ids and element_id:
            invoiced_pack_ids = element_id.pack_of_pack_invoiced_ids + invoiced_pack_ids
            element_id.pack_of_pack_invoiced_ids = self.get_pack_of_pack_invoiced_ids(element_id, invoiced_pack_ids)
            split_packs = True
        if 'pack_invoiced_ids' in element_id._fields and invoiced_pack_ids and element_id:
            invoiced_pack_ids = element_id.pack_invoiced_ids + invoiced_pack_ids
            element_id.pack_invoiced_ids = self.get_pack_invoiced_ids(element_id, invoiced_pack_ids, split_packs)
        if results.get('helperFromModel') == 'lims.analysis':
            analysis_id = request.env['lims.analysis'].browse(results['analysis_id'])
            analysis_id.sudo().compute_costing()
        elif results.get('helperFromModel') == 'lims.analysis.request.sample':
            analysis_request_sample = request.env['lims.analysis.request.sample'].browse(
                results['helperFromId'])
            analysis_request_sample.request_id.analysis_ids.sudo().compute_costing()

    def get_pack_of_pack_invoiced_ids(self, element_id, invoiced_pack_ids):
        return invoiced_pack_ids.filtered(lambda p: p.is_pack_of_pack and p.id not in element_id.pack_of_pack_ids.ids)

    def get_pack_invoiced_ids(self, element_id, invoiced_pack_ids, split_packs=False):
        if split_packs:
            return invoiced_pack_ids.filtered(lambda p: not p.is_pack_of_pack and p.id not in element_id.pack_ids.ids)
        return invoiced_pack_ids.filtered(lambda p: p.id not in element_id.pack_ids.ids)

    def get_parameter_packs_dictonnary(self, data, owned_packs, current_results, only_parameters, element=False):
        res = super().get_parameter_packs_dictonnary(data, owned_packs, current_results, only_parameters, element)
        element = res.get('element')
        current_invoiced_ids = []
        if element and 'pack_invoiced_ids' in element._fields:
            current_invoiced_ids = element.pack_invoiced_ids.ids
            if 'pack_of_pack_invoiced_ids' in element._fields:
                current_invoiced_ids += element.pack_of_pack_invoiced_ids.ids
            current_invoiced_ids = list(set(current_invoiced_ids))
        for element_data in res.get('data'):
            element_data['is_current_invoiced'] = element_data.get('id') and element_data.get(
                'id') in current_invoiced_ids
        return res
