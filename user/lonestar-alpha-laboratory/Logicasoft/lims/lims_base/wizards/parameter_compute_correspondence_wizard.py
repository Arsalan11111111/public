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
from odoo import models, fields, api, exceptions, _
import math
from statistics import mean, median, stdev, variance
from odoo.tools.safe_eval import safe_eval
import re


COMPUTE_FUNCTIONS = {
    '(min\((\[[0-9\.\, ]+\])\))': min,
    '(max\((\[[0-9\.\, ]+\])\))': max,
    '(sum\((\[[0-9\.\, ]+\])\))': sum,
    '(mean\((\[[0-9\.\, ]+\])\))': mean,
    '(median\((\[[0-9\.\, ]+\])\))': median,
    '(stdev\((\[[0-9\.\, ]+\])\))': stdev,
    '(variance\((\[[0-9\.\, ]+\])\))': variance,
    '(log\(([0-9.]+\,[ 0-9]+)\))': lambda vals: math.log(vals[0], vals[1]),
}


class ParameterComputeCorrespondenceWizard(models.TransientModel):
    _name = 'parameter.compute.correspondence.wizard'
    _description = 'Wizard to compute the formula with test values'

    @api.model
    def default_get(self,fields_list):
        res = super().default_get(fields_list)
        id = self.env.context.get("active_id",False)

        if id:
            characteristic_id=self.env['lims.method.parameter.characteristic'].browse(int(id))
            lines=[]
            for line in characteristic_id.correspondence_ids:
                values = {
                    'method_param_charac_id': line.method_param_charac_id.id,
                    'correspondence': line.correspondence,
                    'value_test': 1,
                }
                lines.append((0, 0, values))

            res.update({
                'characteristic_id':id,
                'correspondence_ids':lines,
                'formula':characteristic_id.formula,
                'use_function':characteristic_id.use_function,
            })

        return res

    characteristic_id=fields.Many2one('lims.method.parameter.characteristic',string = "Parameter Characteristic",readonly=True)
    correspondence_ids = fields.One2many('parameter.compute.correspondence.wizard.line', 'link_id','Table of correspondences')
    use_function = fields.Boolean('Use function',readonly=True)
    formula=fields.Char()
    formula_result=fields.Float('Formula result',default=0)
    message_error=fields.Text(string="Error message",readonly=True)

    @api.onchange('correspondence_ids', 'formula')
    def test_formula(self):
        self.message_error=''
        if self.formula:
            formula = self.formula
            correspondences = re.findall('\[([A-Za-z0-9éèàçîêù]+)\]*', formula)

            if sorted(set(correspondences)) == sorted(self.correspondence_ids.mapped('correspondence')):
                for correspondence in correspondences:
                    lines = self.correspondence_ids.filtered(lambda c: c.correspondence == correspondence)
                    values_test = lines.mapped('value_test')
                    value_test = values_test[0]
                    formula = formula.replace('[' + correspondence + ']', str(value_test))
                if self.use_function:
                    for funct in COMPUTE_FUNCTIONS:
                        parts = re.findall(funct, formula)
                        for sub_formula in parts:
                            formula_to_replace = sub_formula[0]
                            try:
                                formula_to_compute = safe_eval(sub_formula[1])
                                formula_res = COMPUTE_FUNCTIONS[funct](formula_to_compute)
                                formula = formula.replace(formula_to_replace, str(formula_res))
                            except Exception as error:
                                self.message_error = str(error)
                                return
                try:
                    value = safe_eval(formula)
                except Exception as error:
                    self.message_error = str(error)
                    return

                try:
                    value = float(value)
                except:
                    self.message_error=_("Formula must return a number")

                self.formula_result = value
            else:
                self.message_error=_("Error on computed parameter : elements inside brackets in the formula don\'t match elements indicated inside the correspondence\'s table")
        else:
            self.message_error=_('There is no formula')

    def save_formula(self):
        self.characteristic_id.write({'formula':self.formula})

class AddParametersWizardLine(models.TransientModel):
    _name = 'parameter.compute.correspondence.wizard.line'
    _description = 'Line for the wizard to encode the test values'

    link_id = fields.Many2one('parameter.compute.correspondence.wizard', 'Link to wizard')
    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter Characteristic',readonly=True)
    correspondence = fields.Char(string="Correspondence",readonly=True)
    value_test = fields.Float(string="Value test")
