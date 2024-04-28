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
from odoo import models, fields, api


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    regulation_ids = fields.Many2many('lims.regulation', string='Regulations')
    matrix_id_domain_ids = fields.Many2many('lims.matrix', compute='compute_matrix_id_domain_ids')

    @api.depends('regulation_ids')
    def compute_matrix_id_domain_ids(self):
        """
        Change base function to apply to new field regulation_ids instead of regulation_id
        """
        method_parameter_characteristic_ids = self.env['lims.method.parameter.characteristic'].search([])
        all_matrix_ids = self.env['lims.matrix'].search([])
        for record in self:
            if record.regulation_ids:
                matrix_ids = method_parameter_characteristic_ids.filtered(
                    lambda m: m.regulation_id.id in record.regulation_ids.ids
                ).mapped('matrix_id')
            else:
                matrix_ids = all_matrix_ids
            record.matrix_id_domain_ids = [(6, 0, matrix_ids.ids)]

    def get_value_of_result_id(self, result_id):
        res = super(LimsAnalysis, self).get_value_of_result_id(result_id)
        res.update({
            'regulation_id': result_id.method_param_charac_id.regulation_id
        })
        return res

    def get_regulation(self):
        return self.regulation_ids.ids

    def set_regulation(self, pack_ids=None, param_ids=None):
        packs = pack_ids and pack_ids.filtered(
            lambda p: p.state == 'validated' and p.matrix_id == self.matrix_id and p.regulation_id)
        parameters = param_ids and param_ids.filtered(
            lambda p: p.state == 'validated' and p.matrix_id == self.matrix_id and p.regulation_id)
        for record in self.filtered(lambda a: not a.get_regulation()):
            regulation_ids = self.env['lims.regulation']
            if packs:
                regulation_ids += pack_ids.regulation_id
            if parameters:
                regulation_ids += parameters.regulation_id
            record.regulation_ids = regulation_ids
