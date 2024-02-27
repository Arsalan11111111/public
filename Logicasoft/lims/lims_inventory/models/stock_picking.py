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
from odoo import fields, models, api, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_states(self):
        return [
            ('all_conform', 'All Conform'),
            ('all_not_conform', 'All Not Conform'),
            ('both', 'Both'),
        ]

    rel_create_analysis = fields.Boolean(related='picking_type_id.create_analysis',
                                         help="This is the 'Create Analysis' button of his picking type.")
    nb_analysis = fields.Integer(compute='compute_nb_analysis')
    analysis_states = fields.Selection(selection='get_states', compute='get_state_analysis',
                                       help="If among all the analysis linked to the move lines of these "
                                            "stock moves without package, if they are all 'conform'/'not conform', "
                                            "this field will get 'conform'/'not conform' value respectively. "
                                            "Nonetheless, If they are some 'conform' and 'not conform', "
                                            "it will be 'both' value.")

    def get_state_analysis(self):
        self.ensure_one()
        analysis_ids = self.get_picking_analysis()
        states = analysis_ids.mapped('state')

        if 1 == len(set(states)):
            if 'conform' in states:
                self.analysis_states = 'all_conform'
            elif 'not_conform' in states:
                self.analysis_states = 'all_not_conform'
            else:
                self.analysis_states = False
        elif ('conform' in states) and ('not_conform' in states):
            self.analysis_states = 'both'
        else:
            self.analysis_states = False

    def get_picking_analysis(self):
        return self.move_ids_without_package.mapped('move_line_ids.analysis_ids')

    def compute_nb_analysis(self):
        for record in self:
            record.nb_analysis = len(record.get_picking_analysis())

    def open_analysis(self):
        self.ensure_one()
        analysis = self.get_picking_analysis()
        return {
            'name': _('Analysis'),
            'domain': [('id', 'in', analysis.ids)],
            'res_model': 'lims.analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot,graph',
            'view_type': 'form',
        }
