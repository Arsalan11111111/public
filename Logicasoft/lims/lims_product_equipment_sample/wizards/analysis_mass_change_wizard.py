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


class AnalysisMassChangeWizard(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard'

    equipment_ids = fields.Many2many('maintenance.equipment', string='Equipments')
    reagent_ids = fields.Many2many('product.product', string='Reagents')

    first_edit_equipment = fields.Boolean()
    first_edit_reagent = fields.Boolean()

    @api.model
    def default_get(self, fields_list):
        res = super(AnalysisMassChangeWizard, self).default_get(fields_list)
        if 'line_ids' in res:
            line_ids = res['line_ids']
            for line in line_ids:
                analysis_id = self.env['lims.analysis'].browse(line[2].get('analysis_id'))
                line[2].update({
                    'equipment_ids': [Command.set(analysis_id.analysis_equipments_ids.equipment_id.ids)],
                    'reagent_ids': [Command.set(analysis_id.analysis_reagent_ids.product_id.ids)]
                })
        return res

    @api.onchange('equipment_ids')
    def onchange_equipments(self):
        if self.first_edit_equipment:
            self.line_ids.update({'equipment_ids': [(6, 0, self.equipment_ids.ids)]})
        else:
            self.update({'first_edit_equipment': True})

    @api.onchange('reagent_ids')
    def onchange_reagent_ids(self):
        if self.first_edit_reagent:
            self.line_ids.update({'reagent_ids': [(6, 0, self.reagent_ids.ids)]})
        else:
            self.update({'first_edit_reagent': True})

    def save_analysis(self):
        res = super(AnalysisMassChangeWizard, self).save_analysis()
        LimsEquipment = self.env['lims.maintenance.equipment']
        LimsReagent = self.env['lims.reagent.stock']
        for line in self.line_ids:
            old_lims_equipments = line.analysis_id.analysis_equipments_ids.filtered(
                lambda e: e.equipment_id in line.equipment_ids
            )

            new_lims_equipments = LimsEquipment
            new_equipments = line.equipment_ids - line.analysis_id.analysis_equipments_ids.equipment_id
            for equipment in new_equipments:
                new_lims_equipments += new_lims_equipments.create({
                    'equipment_id': equipment.id,
                    'origin_analysis_id': line.analysis_id.id
                })

            old_lims_reagents = line.analysis_id.analysis_reagent_ids.filtered(
                lambda r: r.product_id in line.reagent_ids
            )

            new_lims_reagents = LimsReagent
            new_reagents = line.reagent_ids - line.analysis_id.analysis_reagent_ids.product_id
            for reagent in new_reagents:
                new_lims_reagents += new_lims_reagents.create({
                    'product_id': reagent.id,
                    'origin_analysis_id': line.analysis_id.id
                })

            line.analysis_id.write({
                'analysis_equipments_ids': [(6, 0, old_lims_equipments.ids + new_lims_equipments.ids)],
                'analysis_reagent_ids': [(6, 0, old_lims_reagents.ids + new_lims_reagents.ids)]
            })
        return res


class AnalysisMassChangeWizardLine(models.TransientModel):
    _inherit = 'analysis.mass.change.wizard.line'

    equipment_ids = fields.Many2many('maintenance.equipment', string='Equipments')
    reagent_ids = fields.Many2many('product.product', string='Reagents')
