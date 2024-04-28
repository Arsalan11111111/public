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
from odoo import models


class LimsAnalysisRequest(models.Model):
    _inherit = 'lims.analysis.request'

    def generate_request_sample_line(self):
        """"
        Override lims_base function to authorize multiple regulations on one sample line
        """
        vals_list = []
        request_sample_obj = self.env['lims.analysis.request.sample']
        update_details = False
        for product_id in self.product_ids:
            all_pack = self.env['lims.parameter.pack']
            all_pack += product_id.pack_ids.filtered(lambda p: not p.is_pack_of_pack)
            all_pack += product_id.pack_ids.filtered(lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id')
            regulations = all_pack.mapped('regulation_id') + product_id.method_param_charac_ids.mapped('regulation_id')
            i = product_id.qty - len(
                product_id.request_sample_ids)
            # check if line need to be updated if new pack or new param charac
            if not i and product_id.request_sample_ids:
                request_sample_ids = product_id.request_sample_ids
                for request_sample_id in request_sample_ids:
                    if len(request_sample_id.pack_ids) != len(
                            product_id.pack_ids.filtered(lambda p: not p.is_pack_of_pack)):
                        pack_ids = product_id.pack_ids.filtered(
                            lambda p: not p.is_pack_of_pack)
                        pack_ids += product_id.pack_ids.filtered(
                            lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id')
                        request_sample_id.pack_ids = pack_ids
                    if len(request_sample_id.method_param_charac_ids) != len(product_id.method_param_charac_ids):
                        request_sample_id.method_param_charac_ids = product_id.method_param_charac_ids
            while i > 0:
                vals = self.get_values_for_create_sample(product_id, all_pack, regulations)
                vals_list.append(vals)
                i -= 1
        request_sample_obj.create(vals_list)

    def get_values_for_create_sample(self, product_id, packs, regulations):
        res = super(LimsAnalysisRequest, self).get_values_for_create_sample(product_id, {}, regulations[0] if regulations else False)
        if res:
            res.update({
                'regulation_ids': [(4, reg.id) for reg in regulations],
                'pack_ids': [(4, pack.id) for pack in packs],
                'method_param_charac_ids': [(4, method_param_charac_ids.id) for
                                            method_param_charac_ids in product_id.method_param_charac_ids],
            })
        return res

    def add_analysis_values(self, sample_id, sample_info=False):
        res = super().add_analysis_values(sample_id, sample_info)
        res.update({
            'regulation_ids': [(4, regulation_id.id) for regulation_id in sample_id.regulation_ids],
        })
        return res
