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


class LimsMethodParameterCharacteristicEquipment(models.Model):
    _inherit = 'lims.method.parameter.characteristic.equipment'

    def get_single_equipment_for_analysis(self, analysis_id):
        equipment_id = self.filtered(lambda e: e.method_param_charac_id.matrix_id.id == analysis_id.matrix_id.id)
        if len(equipment_id) > 1 and analysis_id.regulation_id:
            equipment_id = self.filtered(lambda e:
                                         e.method_param_charac_id.regulation_id.id == analysis_id.regulation_id.id)
        return equipment_id

    def get_vals_for_result(self):
        self.ensure_one()
        vals = {'equipment_id': self.equipment_id.id}
        if self.loq:
            vals.update({
                'loq': self.loq
            })
        if self.ls:
            vals.update({'ls': self.ls})
        if self.lod:
            vals.update({'lod': self.lod})
        if self.u:
            vals.update({'u': self.u})
        if self.recovery:
            vals.update({'recovery': self.recovery})
        if self.factor:
            vals.update({'dilution_factor': self.factor})
        return vals
