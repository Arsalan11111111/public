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
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo import _


class ParametersHelper(http.Controller):

    def _get_packs(self, vals):
        """
        This method was created and is very useful if you need to override the packs domain
        as requested/needed for different projects.

        :param vals: A dictionary composed of the variables obtained via JS params
            -> id, model, analysis_id, type

        Here is an example on how to override it the easy way:

        from odoo.addons.lims_base.controllers.parameters_helper import ParametersHelper
        from odoo.http import request

        class MyClassName(ParametersHelper):

            def _get_packs(self, data):
                # Overriding / no need to call super / change the domain below
                return request.env['lims.parameter.pack'].search(
                    [('matrix_id', '=', data['id']), ('state', '=', 'validated')])
        """
        domain = ['&', ('matrix_id', '=', vals['matrix_id']), ('state', '=', 'validated')]
        if vals.get('object') and vals['object'].get_regulation():
            regulation_ids = vals['object'].get_regulation()
            domain = expression.AND([domain, [('regulation_id', 'in', regulation_ids)]])
        return request.env['lims.parameter.pack'].search(domain)

    def _get_result_info(self, base_obj):
        return {
            'id': base_obj.id,
            'name': base_obj.tech_name,
            'method': base_obj.method_id.name,
            'parameter_id': base_obj.parameter_id.name,
            'format': dict(request.env['lims.parameter'].with_context(
                lang=request.env.user.lang).get_selection_format()).get(base_obj.format),
            'department_id': base_obj.department_id.name,
            'laboratory_id': base_obj.laboratory_id.name,
        }

    def _get_pack_info(self, base_obj):
        return {
            'id': base_obj.id,
            'name': base_obj.display_name,
            'display_name': base_obj.display_name,
        }

    def _get_parameters_domain(self, matrix_id, all_parameters_ids, obj):
        """
        Get domain to select which parameters to propose on the helper
        :param matrix_id: id of the matrix
        :param all_parameters_ids: list of parameters already in packs
        :param obj: record of current object (lims.analysis, lims.request.product.pack or lims.analysis.request.sample)
        (not used here, but can be used by inheriting modules to restrain domain)
        :return:
        """
        domain = [
            ('matrix_id', '=', matrix_id),
            ('id', 'not in', all_parameters_ids),
            ('state', '=', 'validated')
        ]
        regulation_ids = obj.get_regulation()
        if regulation_ids:
            domain = expression.AND([domain, [('regulation_id', 'in', regulation_ids)]])
        return domain

    @http.route('/web/parameters_helper/get_parameter_packs', type='json', auth='user')
    def get_parameter_packs(self, model, model_id, helper_from_model, helper_from_id, matrix_id, analysis_id):
        data = []
        current_results = []
        owned_packs = []
        # Case 1 : Design for lims.analysis
        if model == helper_from_model:
            element = request.env[model].browse(model_id)
        # Case 2 : For all others models
        else:
            element = request.env[helper_from_model].browse(helper_from_id)
        if element:
            owned_packs.extend(self._get_pack_info(pack) for pack in element.pack_ids)
            current_results.extend(self._get_result_info(parameter) for parameter in element.method_param_charac_ids)

        all_parameters_ids = []
        packs = self._get_packs({
            'model': model,
            'model_id': model_id,
            'helper_from_model': helper_from_model,
            'helper_from_id': helper_from_id,
            'matrix_id': matrix_id,
            'analysis_id': analysis_id,
            'object': element,
        })
        for pack in packs:
            parameters = []
            param_in_pack = []
            for parameter in pack.parameter_ids.filtered(lambda x: x.active and x.rel_state == 'validated'):
                if parameter.method_param_charac_id.id not in param_in_pack:
                    parameters.append(self._get_result_info(parameter.method_param_charac_id))
                    param_in_pack.append(parameter.method_param_charac_id.id)
            if pack.is_pack_of_pack:
                for sub_pack in pack.mapped('pack_of_pack_ids').filtered(
                        lambda x: x.rel_active and x.rel_state == 'validated').pack_id:
                    parameters, param_in_pack = self.add_sub_parameters(sub_pack, parameters, param_in_pack)
            pack_info_dict = self._get_pack_info(pack)
            pack_info_dict['parameters'] = parameters
            data.append(pack_info_dict)
            [all_parameters_ids.append(x) for x in param_in_pack]
        all_parameters = request.env['lims.method.parameter.characteristic'].search_read(
            self._get_parameters_domain(matrix_id, all_parameters_ids, element),
            fields=['id', 'tech_name'])
        return self.get_parameter_packs_dictonnary(data, owned_packs, current_results, all_parameters, element)

    def get_parameter_packs_dictonnary(self, data, owned_packs, current_results, only_parameters, element=False):
        return {
            'data': data,
            'owned_packs': owned_packs,
            'current_results': current_results,
            'only_parameters': only_parameters,
            'element': element or False,
        }

    def add_sub_parameters(self, pack, parameters, param_in_pack):
        if pack.is_pack_of_pack:
            for sub_pack in pack.mapped('pack_of_pack_ids').filtered(
                    lambda x: x.rel_active and x.rel_state == 'validated').pack_id:
                if sub_pack.is_pack_of_pack:
                    parameters, param_in_pack = self.add_sub_parameters(sub_pack, parameters, param_in_pack)
                else:
                    for parameter in sub_pack.parameter_ids.filtered(lambda x: x.active and x.rel_state == 'validated'):
                        if parameter.method_param_charac_id.id not in param_in_pack:
                            parameters.append({
                                'id': parameter.method_param_charac_id.id,
                                'name': parameter.method_param_charac_id.tech_name,
                            })
                            param_in_pack.append(parameter.method_param_charac_id.id)
        else:
            for parameter in pack.parameter_ids.filtered(lambda x: x.active and x.rel_state == 'validated'):
                if parameter.method_param_charac_id.id not in param_in_pack:
                    parameters.append({
                        'id': parameter.method_param_charac_id.id,
                        'name': parameter.method_param_charac_id.tech_name,
                    })
                    param_in_pack.append(parameter.method_param_charac_id.id)

        return parameters, param_in_pack

    @http.route('/web/parameters_helper/create_results', type='json', auth='user')
    def create_results(self, results):
        """
        Main route to add element directly on analysis (if linked or model), or just add possible pack and parameters.
        :param results:
        :return:
        """
        datas = results.get('lims_datas')
        param_ids = False
        pack_ids = False
        if datas:
            param_ids = datas.get('parameter') and request.env['lims.method.parameter.characteristic'].browse(
                datas.get('parameter'))
            pack_ids = datas.get('pack') and request.env['lims.parameter.pack'].browse(datas.get('pack'))
        element_id = False
        analysis_id = False
        # First try to add to the analysis (Lims.analysis) or linked analysis.
        if results.get('model') == results.get('helperFromModel') or results.get('analysis_id'):
            analysis_id = request.env['lims.analysis'].browse(results['analysis_id'])
            pack_ids, param_ids = analysis_id.add_parameters_and_packs(pack_ids, param_ids)

        # Second : Add selected elements, or new added element on lims.analysis.
        if results.get('model') != results.get('helperFromModel'):
            element_id = request.env[results['helperFromModel']].browse(results['helperFromId'])
            element_id_pack_of_pack_ids = False
            if 'pack_of_pack_ids' in element_id._fields and pack_ids:
                element_id.pack_of_pack_ids, pack_form_pack_of_packs = self.get_all_pack_of_packs(pack_ids, element_id)
                pack_ids += pack_form_pack_of_packs
                element_id_pack_of_pack_ids = element_id.pack_of_pack_ids
            if 'pack_ids' in element_id._fields and pack_ids:
                element_id.pack_ids = self.get_all_packs(pack_ids, element_id, element_id_pack_of_pack_ids)
            if 'method_param_charac_ids' in element_id._fields and param_ids:
                element_id.method_param_charac_ids = self.get_all_parameters(param_ids, element_id)
        return element_id or analysis_id or False


    def get_all_pack_of_packs(self, pack_ids, element_id):
        """
        Get all pack of packs previously added and currently added
        And extract new packs form the currently added pack of packs
        :param pack_ids:
        :param element_id:
        :return:
        """
        pack_of_pack_ids = pack_ids.filtered(
            lambda p: p.is_pack_of_pack and p.id not in element_id.pack_of_pack_ids.ids)
        list_pack_of_pack_ids = list(pack_of_pack_ids)
        for pack_of_pack in list_pack_of_pack_ids:
            for pack_of_pack_line in pack_of_pack.pack_of_pack_ids:
                if not pack_of_pack_line.pack_id.is_pack_of_pack and pack_of_pack_line.pack_id.id not in pack_ids.ids:
                    pack_ids += pack_of_pack_line.pack_id
                elif pack_of_pack_line.pack_id.id not in pack_of_pack_ids.ids:
                    pack_of_pack_ids += pack_of_pack_line.pack_id
                    list_pack_of_pack_ids.append(pack_of_pack_line.pack_id)
        element_pack_of_packs = element_id.pack_of_pack_ids + pack_of_pack_ids
        return element_pack_of_packs, pack_ids

    def get_all_packs(self, pack_ids, element_id, pack_of_pack_ids=False):
        """
        Get all pack previously added and currently added.
        :param pack_ids:
        :param element_id:
        :param pack_of_pack_ids:
        :return:
        """
        if not pack_of_pack_ids:
            pack_of_pack_ids = request.env['lims.parameter.pack']
        pack_ids = pack_ids.filtered(lambda p: p.id not in element_id.pack_ids.ids and p.id not in pack_of_pack_ids.ids)
        element_packs = element_id.pack_ids
        element_packs += pack_ids
        return element_packs

    def get_all_parameters(self, param_ids, element_id):
        """
        Get all parameters previously added and currently added.
        :param param_ids:
        :param element_id:
        :return:
        """
        element_id.method_param_charac_ids += param_ids.filtered(
            lambda p: p.id not in element_id.method_param_charac_ids.ids)
        return element_id.method_param_charac_ids
