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

from datetime import datetime, timedelta
from odoo import Command
import odoo.tests
from odoo.tests.common import TransactionCase, SingleTransactionCase, tagged, users, Form
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


@tagged('lgk', 'lims')
class TestMaintenanceEquipment(TransactionCase):
    ''' The goal of this class is to test the manitenance.equipment model
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.user.company_id.id

    @users('lims_maintenance_demo')
    def test_01_create_minimal_maintenance_equipment(self):
        ''' Create a simple maintenance.equipment '''
        equipment_minimal = self.env['maintenance.equipment'].create({
            'name': 'Equipment 1',
            'effective_date': datetime.now(),
        })
        self.assertTrue(equipment_minimal)

    def _get_complete_maintenance_equipment_data(self):
        ref = self.env.ref
        equipment_complete_data = {
            'name': '',
            'effective_date': datetime.now(),
            'company_id': self.company_id,
            'technician_user_id': self.env.ref('base.user_demo').id,
            'owner_user_id': ref('base.user_demo').id,
            'category_id': ref('maintenance.equipment_phone').id,
            'partner_id': ref('lims_base.demo_lims_partner_1').id,
            'partner_ref': "demo_lims_partner_1",
            'location': "Belgium",
            'model': "T12",
            "serial_no": "1234567890123",
            'assign_date': datetime.now(),
            'effective_date': datetime.now(),
            'cost': 123.45,
            'note': "<p>a note</p>",
            'warranty_date': datetime.now() + timedelta(days=365),
            'color': 1,
            'scrap_date': datetime.now(),
            'maintenance_ids': [Command.link(ref('maintenance.m_request_6').id)],
            'period': 365,
            'maintenance_team_id': ref('maintenance.equipment_team_maintenance').id,
            'maintenance_duration': 2,

        }
        return equipment_complete_data

    @users('lims_maintenance_demo')
    def test_02_create_complete_maintenance_equipment(self):
        ''' Create a complete maintenance.equipment without LIMS fields'''
        equipment_complete_data = self._get_complete_maintenance_equipment_data()
        equipment_complete = self.env['maintenance.equipment'].create(equipment_complete_data)
        self.assertTrue(equipment_complete)

    @users('lims_maintenance_demo')
    def test_03_create_lims_maintenance_equipment(self):
        ''' Create a complete maintenance.equipment with LIMS fields'''
        ref = self.env.ref

        traceability_type = ref('lims_maintenance.demo_equipment_traceability_type_1')
        equipment_complete_data = self._get_complete_maintenance_equipment_data()
        equipment_complete_data.update({
            'is_laboratory': True,
            'laboratory_id': ref('lims_base.default_laboratory').id,
            'accredited': True,
            'traceability_type_id': traceability_type.id,
            'mpe': "MPE1",
            'internal_ref': "REF1",
            'laboratory_state': 'draft',
        })
        equipment_complete = self.env['maintenance.equipment'].create(equipment_complete_data)
        self.assertTrue(equipment_complete)

    @users('maintenance_no_lims_demo')
    def test_04_create_lims_maintenance_equipment(self):
        ''' using a form, create a maintenance.equipment '''
        ref = self.env.ref
        val_effective_date = datetime.now().date()

        f = Form(self.env['maintenance.equipment'])
        f.name = 'Equipment 2'
        f.effective_date = val_effective_date

        eq1 = f.save()
        self.assertRecordValues(eq1, [{'effective_date': val_effective_date}])

