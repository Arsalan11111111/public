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
from odoo import models, fields, api, _, exceptions


class SopMassChangeWizard(models.TransientModel):
    _inherit = 'sop.mass.change.wizard'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', domain=[('is_laboratory', '=', True)])

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.line_ids.update({'equipment_id': self.equipment_id.id})

    def do_confirm(self):
        res = super(SopMassChangeWizard, self).do_confirm()
        values = self.line_ids.mapped('equipment_id')
        for equipment_id in values:
            self.line_ids.filtered(lambda l: l.equipment_id == equipment_id).mapped('sop_id').write({
                'equipment_id': equipment_id.id
            })
        return res


class SopMassChangeWizardLine(models.TransientModel):
    _inherit = 'sop.mass.change.wizard.line'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', domain=[('is_laboratory', '=', True)])
