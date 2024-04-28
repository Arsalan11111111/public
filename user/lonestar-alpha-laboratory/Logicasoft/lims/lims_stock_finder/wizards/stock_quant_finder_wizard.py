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
from odoo import models, fields, api, Command
from odoo.osv import expression

import re

TERM_OPERATORS_CONVERSION = {
    '<': '>',
    '>': '<',
    '<=': '>=',
    '>=': '<=',
    '=': '='
}


def eval_float_value(value_str):
    evaluation = False
    try:
        float(value_str)
        evaluation = True
    finally:
        return evaluation


class LimsStockFinderQuantFinderWizard(models.TransientModel):
    _name = 'lims_stock_finder.quant.finder.wizard'
    _description = 'Stock quant finder wizard'
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        if active_model == 'stock.quant' and active_ids:
            product_ids = self.env['stock.quant'].browse(active_ids).product_id
            if product_ids:
                res.update({
                    'product_ids': [Command.set(product_ids.ids)]
                })
        return res

    product_ids = fields.Many2many('product.product')
    quantity = fields.Float(help='The minimal quantity to be present in filtered list')
    criteria_ids = fields.One2many('lims_stock_finder.quant.finder.criteria', 'finder_id')
    stock_quant_ids = fields.Many2many('stock.quant', readonly=True)
    analysis_ids = fields.Many2many('lims.analysis')

    def get_stock_quant_domain(self):
        return [('product_id', 'in', self.product_ids.ids), ('on_hand', '=', True)]

    def get_analysis_domain(self):
        return [('rel_type', '=', 'validated2'), ('product_id', 'in', self.product_ids.ids)]

    def find(self):
        analysis_ids = self.analysis_ids.filter_analysis_with_criteria(self.analysis_ids,
                                                                       domain=self.get_analysis_domain(),
                                                                       criteria_ids=self.criteria_ids)
        quant_ids = self.env['stock.quant'].search(self.get_stock_quant_domain())
        quant_ids = self._filter_quant_by_available_quantity(quant_ids)
        filtered_quant_ids = self.env['stock.quant']
        if analysis_ids:
            filtered_quant_ids += quant_ids.filtered(lambda q: q.lot_id and q.lot_id.analysis_ids and bool(
                set(analysis_ids.ids) & set(q.lot_id.analysis_ids.ids)))
        else:
            filtered_quant_ids = quant_ids
        return self._get_action(filtered_quant_ids.ids)

    def _filter_quant_by_available_quantity(self, quant_ids):
        self.ensure_one()
        if self.quantity:
            quant_ids = quant_ids.filtered(
                lambda q: abs(self.quantity) <= (q.quantity - q.reserved_quantity))
        return quant_ids

    @api.onchange('product_ids', 'quantity')
    def onchange_stock_quant_ids(self):
        self.stock_quant_ids = self._filter_quant_by_available_quantity(
            self.env['stock.quant'].search(self.get_stock_quant_domain()))

    @api.onchange('stock_quant_ids')
    def onchange_analysis_ids(self):
        self.analysis_ids = self.env['lims.analysis'].search(self.get_analysis_domain())

    def _get_action(self, ids=None):
        if ids is None:
            ids = []
        action = self.env['stock.quant'].with_context(
            search_default_internal_loc=1,
            search_default_productgroup=1,
            search_default_locationgroup=1,
        ).action_view_quants()
        action['domain'] = [('id', 'in', ids)]
        return action


class LimsStockFinderQuantFinderCriteria(models.TransientModel):
    _name = 'lims_stock_finder.quant.finder.criteria'
    _description = 'Stock quant finder criteria'
    _order = 'sequence, id'


    sequence = fields.Integer(default=10)
    finder_id = fields.Many2one('lims_stock_finder.quant.finder.wizard')
    parameter_id = fields.Many2one('lims.parameter')
    rel_format = fields.Selection(related='parameter_id.format')
    rel_result_value_ids = fields.Many2many(related='parameter_id.result_value_ids')
    criteria = fields.Char()
    state = fields.Selection('get_selection_state', 'State', help="This is the state of the conformity of that result.")
    criteria_evaluated = fields.Char(compute='convert_criteria')

    def get_selection_state(self):
        return self.env['lims.analysis.result'].get_selection_state()

    @api.depends('parameter_id', 'criteria', 'state')
    def convert_criteria(self):
        for record in self:
            criteria_evaluated = False
            domain = []
            if record.criteria and record.parameter_id:
                criteria_evaluated = record._convert_string_criteria(criteria_evaluated, domain)
            if record.state and record.parameter_id:
                criteria_evaluated = record._convert_state_criteria(criteria_evaluated)
            criteria_evaluated = criteria_evaluated and record._add_final_cirteria(criteria_evaluated)
            record.criteria_evaluated = criteria_evaluated if criteria_evaluated != list() else False

    def _convert_string_criteria(self, string_criteria, domain):
        self.ensure_one()
        if self.rel_format == 'se':
            string_criteria = self.criteria_selection_evaluate(self.criteria,
                                                               self.parameter_id.result_value_ids,
                                                               self.env.user.lang)
            string_criteria = self.generate_se_domain(string_criteria, domain)
        elif self.rel_format in ['nu', 'ca']:
            string_criteria = self.clean_numeric_criteria(self.criteria)
            string_criteria = self.criteria_numeric_evaluate(string_criteria)
            string_criteria = self.generate_nu_domain(string_criteria, domain,
                                             'value' if self.rel_format == 'ca' else False)
        elif self.rel_format == 'tx':
            string_criteria = self.generate_tx_domain(self.criteria, domain)
        return string_criteria

    def _convert_state_criteria(self, domain):
        self.ensure_one()
        return expression.AND([domain, [('state', '=', self.state)]])

    def _add_final_cirteria(self, domain):
        if domain:
            domain = expression.AND(
                [[('method_param_charac_id.parameter_id', '=', self.parameter_id.id)], domain])
        return domain

    @staticmethod
    def generate_tx_domain(criteria, domain):
        return expression.AND([domain, [('value', 'ilike', criteria)]])

    @staticmethod
    def generate_se_domain(criteria, domain):
        if not criteria:
            criteria = False
        if criteria and len(criteria):
            domain = expression.OR([domain, [('value_id.id', 'in', criteria)]])
        return domain

    @staticmethod
    def generate_nu_domain(criteria, domain, result_value='corrected_value'):
        if not result_value:
            result_value = 'corrected_value'
        if (criteria and len(criteria) == 5 and isinstance(criteria[0], float) and
                criteria[1] in ['=', '<', '<=', '>', '>='] and criteria[2] == 'X' and
                criteria[3] in ['=', '<', '<=', '>', '>='] and isinstance(criteria[4], float)):
            criteria[1] = TERM_OPERATORS_CONVERSION[criteria[1]]
            domain = expression.AND([domain, [(result_value, criteria[1], criteria[0])]])
            criteria = criteria[2:]
        if criteria and len(criteria) == 2:
            criteria.insert(0, 'X')
        if (criteria and len(criteria) == 3 and criteria[1] in ['=', '<', '<=', '>', '>=']
                and isinstance(criteria[2], float)):
            domain = expression.AND([domain, [(result_value, criteria[1], criteria[2])]])
        return domain

    @staticmethod
    def criteria_numeric_evaluate(criteria):
        if not criteria:
            criteria = []
        criteria_evaluated = None
        if criteria and len(criteria) == 3:
            if criteria[1] == '+-' and eval_float_value(criteria[0]) and eval_float_value(criteria[2]):
                # 12.3 +- 3
                criteria[0] = float(criteria[0])
                criteria[2] = abs(float(criteria[2]))
                criteria_evaluated = [criteria[0] - criteria[2], '<=', 'X', '<=', criteria[0] + criteria[2]]
            elif criteria[1] == '%' and eval_float_value(criteria[0]) and eval_float_value(criteria[2]):
                # 12.3 % 30
                criteria[0] = float(criteria[0])
                criteria[2] = criteria[0] * abs(float(criteria[2])) / 100
                criteria_evaluated = [criteria[0] - criteria[2], '<=', 'X', '<=', criteria[0] + criteria[2]]
            elif criteria[0] == 'X' and eval_float_value(criteria[2]):
                # x > 12.33
                criteria[2] = float(criteria[2])
                criteria_evaluated = criteria
        elif criteria and len(criteria) == 5 and criteria[2] == 'X' and eval_float_value(
                criteria[0]) and eval_float_value(criteria[4]):
            # 12.3 > x < 12.4
            criteria[0] = float(criteria[0])
            criteria[4] = float(criteria[4])
            criteria_evaluated = criteria
        elif criteria and len(criteria) == 2 and eval_float_value(criteria[1]) and TERM_OPERATORS_CONVERSION.get(
                criteria[0]):
            # >15 (== X>15)
            criteria[1] = float(criteria[1])
            criteria_evaluated = criteria
        return criteria_evaluated

    @staticmethod
    def clean_numeric_criteria(string):
        string = string.replace('x', 'X')
        string = string.replace(',', '.')
        string = string.replace('-+', '+-')
        string = string.replace('±', '+-')
        string = string.replace('≥', '>=')
        string = string.replace('=>', '>=')
        string = string.replace('=<', '<=')
        string = string.replace('≤', '<=')
        string = ''.join(re.findall(r"[0-9xX><=+%\-.]+", string))
        string = re.findall(r"[-+]?\d*\.\d+|\d+|[xX]|[<>=]+|[%]|[-+]{1,2}", string)
        return string

    @staticmethod
    def criteria_selection_evaluate(string, result_value_ids=None, lang='en_US'):
        ids = set()
        criteria_ids = re.split(r";", string)
        result_value_ids = result_value_ids.with_context(lang=lang)
        if criteria_ids and result_value_ids:
            for criteria_id in criteria_ids:
                for result_value_id in result_value_ids:
                    if criteria_id in result_value_id.name:
                        ids.add(result_value_id.id)
        return list(ids) or ''
