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


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    is_laboratory = fields.Boolean('Used in Laboratory ?')
    laboratory_id = fields.Many2one('lims.laboratory', 'Laboratory')
    accredited = fields.Boolean('Accreditation')
    parent_id = fields.Many2one('maintenance.equipment', string='Parent')
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string='Children')
    traceability_type_id = fields.Many2one('equipment.traceability.type', string='Type of traceability')
    mpe = fields.Char('MPE')
    internal_ref = fields.Char('Internal reference')
    laboratory_state = fields.Selection([('draft', 'Draft'), ('in_service', 'In service'),
                                         ('out_of_service', 'Out of service')], 'Laboratory State', index=True,
                                        help='The status of the labware determines whether it can be used. Only the '
                                             'equipment identified as "In service" will be available when selecting '
                                             'equipment for a test in the Lims.', tracking=True)
    is_gmp = fields.Boolean(string="GMP")
    gamp_category_id = fields.Many2one('gamp.category', string="Category GAMP")
