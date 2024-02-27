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


class LimsMethodParameterCharacteristicEquipment(models.Model):
    _name = 'lims.method.parameter.characteristic.equipment'
    _description = 'Lims Method Parameter Characteristic Equipment'
    _rec_name = 'equipment_id'

    method_param_charac_id = fields.Many2one('lims.method.parameter.characteristic', 'Parameter', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', help="Only laboratory equipment is available")
    reference = fields.Char('Reference')
    loq = fields.Float('LOQ', digits='Analysis Result')
    ls = fields.Float('LS', digits='Analysis Result')
    lod = fields.Float('LOD', digits='Analysis Result')
    u = fields.Float('U', digits='Analysis Result')
    recovery = fields.Float('Recovery')
    factor = fields.Float('Factor', digits='Analysis Result')
    mandatory = fields.Boolean('Mandatory')
    comment = fields.Char('Comment')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory', related='equipment_id.laboratory_id',
                                    readonly=True, help="The laboratory of the equipment.")
    rel_laboratory_state = fields.Selection(related='equipment_id.laboratory_state',
                                            help="The 'Laboratory state' of the equipment.")

    def update_result_vals(self, result_vals):
        self.ensure_one()
        if self.loq:
            result_vals.update({'loq': self.loq})
        if self.lod:
            result_vals.update({'lod': self.lod})
        if self.ls:
            result_vals.update({'ls': self.ls})
        if self.u:
            result_vals.update({'u': self.u})
        if self.recovery:
            result_vals.update({'recovery': self.recovery})
        if self.factor:
            result_vals.update({'dilution_factor': self.factor})
