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
from odoo import fields, models


class LimsAnalysisNumericResult(models.Model):
    _inherit = 'lims.analysis.numeric.result'

    def write(self, values):
        if 'equipment_id' in values:
            equipment_id = values.get('equipment_id')
            if equipment_id:
                for record in self:
                    res_vals = values.copy()
                    equipment_line_ids = record.method_param_charac_id.method_param_equipment_ids.sudo().filtered(
                        lambda x: x.equipment_id.id == equipment_id and x.laboratory_id == record.rel_laboratory_id)
                    if equipment_line_ids:
                        equipment_line = equipment_line_ids[0]
                        equipment_line.update_result_vals(res_vals)
                    super().write(res_vals)
                # option 2 : equipment is removed
            else:
                for record in self:
                    res_vals = values.copy()
                    record.add_parameter_values(record.method_param_charac_id, res_vals)
                    super().write(res_vals)
        else:
            super().write(values)
        return True
