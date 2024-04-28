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

import datetime
import random
import logging
from operator import itemgetter
from itertools import groupby
from odoo import Command
from odoo.tests.common import TransactionCase, tagged, users, Form
from ..populate.common import SingleTransactionCase, POPULATE_SIZE, REQUEST_SIZES


_logger = logging.getLogger(__name__)


@tagged('lgk', 'lims')
class TestLimsBaseLimsAnalysis(TransactionCase):
    """ The goal of this class is to test the lims.analysis model
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.user.company_id.id

    @users('lims_demo')
    def test_01_create_lims_analysis(self):
        """ Create a simple lims.analysis """
        matrix = self.env.ref('lims_base.demo_matrix_1')
        laboratory = self.env.user.default_laboratory_id
        analysis = self.env['lims.analysis'].create({
            'matrix_id': matrix.id,
            'laboratory_id': laboratory.id,
        })
        self.assertTrue(analysis)

    @users('lims_demo')
    def test_02_form_create_lims_analysis(self):
        """ Use a form to create a lims.analysis """

        matrix = self.env.ref('lims_base.demo_matrix_1')
        regulation = self.env.ref('lims_base.demo_regulation_1')
        val_date_plan = datetime.datetime.strptime('2022-06-30 12:00:00', "%Y-%m-%d %H:%M:%S")

        f = Form(self.env['lims.analysis'])
        f.matrix_id = matrix
        f.regulation_id = regulation
        f.date_plan = val_date_plan
        ana = f.save()
        self.assertRecordValues(ana, [{'date_plan': val_date_plan}])

    @users('lims_demo')
    def test_03_example_assert_record_values(self):
        """ Example of assertRecordValues """

        matrix = self.env.ref('lims_base.demo_matrix_1')
        laboratory = self.env.user.default_laboratory_id

        for _ in range(2):
            analysis = self.env['lims.analysis'].create({
                'matrix_id': matrix.id,
                'laboratory_id': laboratory.id,
                'state': 'init',
            })
            self.assertTrue(analysis)

        records = self.env['lims.analysis'].search([('state', '=', 'init')], limit=2)
        self.assertRecordValues(records, [{'state': 'init'}, {'state': 'init'}])


@tagged('lgk', 'lims', 'populate')
class TestLimsBaseLimsAnalysisRequest(SingleTransactionCase):
    """ The goal of this class is to test the performance lims.analysis.request model
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.user.company_id.id

    def assign_packs_to_requests(self, requests, pack_ids_pool, param_pack_line):
        def assign_pack(request, pack_ids_pool, param_pack_line):
            if not pack_ids_pool:
                return
            group_key = itemgetter(*['matrix_id'])
            pack_lines_by_matrix_id = {
                k.id: list(itr)
                for k, itr in groupby(sorted(param_pack_line, key=group_key), group_key)
            }
            pack_id = pack_ids_pool.pop()
            pack = self.env['lims.request.product.pack'].browse(pack_id)
            pack.request_id = request.id

            pack_lines = pack_lines_by_matrix_id.get(pack.matrix_id.id)
            pack_line_ids_pool = [p.id for p in pack_lines]
            len_lines = len(pack_lines)

            for _ in range(random.randint(0, len_lines)):
                if not pack_line_ids_pool:
                    return

                pack_only = random.choice([True, False])
                if pack_only:
                    # pack, not individual lines
                    line_id = random.choice(pack_line_ids_pool)
                    pack_line_ids_pool.remove(line_id)
                    line_pack_id = self.env['lims.parameter.pack.line'].browse(line_id).pack_id.id
                    pack.write({
                        'method_param_charac_ids': [(Command.link(line_id))],
                        'pack_ids': [(Command.link(line_pack_id))],
                    })
                else:
                    # individual lines
                    line_id = random.choice(pack_line_ids_pool)
                    pack_line_ids_pool.remove(line_id)
                    pack.write({
                        'method_param_charac_ids': [(Command.link(line_id))],
                    })
        # END assign_pack

        for req in requests:
            num_pack = random.randint(1, 5)
            for _ in range(num_pack):
                assign_pack(req, pack_ids_pool, param_pack_line)

    @users('lims_demo')
    def test_01_populate_lims_analysis_request(self):
        """ Populate lims.analysis.request records"""

        requests = self.env['lims.analysis.request']._populate(POPULATE_SIZE)
        self.assertTrue(len(requests) >= REQUEST_SIZES[POPULATE_SIZE] and len(requests) >= REQUEST_SIZES[POPULATE_SIZE] + 1)
        packs = self.env['lims.request.product.pack']._populate(POPULATE_SIZE)
        self.assertTrue(len(packs) >= REQUEST_SIZES[POPULATE_SIZE] and len(requests) >= REQUEST_SIZES[POPULATE_SIZE] + 1)

    @users('lims_demo')
    def test_02_assign_packs_to_lims_analysis_request(self):
        """ Assign packs to lims.analysis.request records"""

        requests = self.env['lims.analysis.request'].search([])
        packs = self.env['lims.request.product.pack'].search([])
        param_pack_line = self.env['lims.parameter.pack.line'].search([])
        self.assign_packs_to_requests(requests, packs.ids, param_pack_line)

    @users('lims_demo')
    def test_03_generate_sample_lines(self):
        """ Generate sample lines"""
        requests = self.env['lims.analysis.request'].search(
            [('product_ids', '!=', False), '|',('product_ids.pack_ids', '!=', False),
             ('product_ids.method_param_charac_ids', '!=', False)])
        for req in requests:
            req.generate_request_sample_line()

    @users('lims_demo')
    def test_04_do_confirmed(self):
        """ Confirm lims.analysis.requests"""

        requests = self.env['lims.analysis.request'].search([])

        ct = 0
        for req in requests:
            # keep a few requests as draft
            if random.randint(0, 9) <= 6:
                req.do_confirmed()

            tot = REQUEST_SIZES[POPULATE_SIZE]
            ct += 1
            if not ct % 100:
                _logger.info(f"Confirmed requests: {ct}/{tot}")

    @users('lims_demo')
    def test_05_create_analysis(self):
        """ Create analysis from lims.analysis.requests"""

        requests = self.env['lims.analysis.request'].search([])

        ct = 0
        for req in requests:
            if req.state == 'accepted' and not req.sample_ids.filtered(lambda s: s.analysis_id):
                # keep a few requests without analysis:
                if random.randint(0, 9) <= 7:
                    # generate analysis
                    wiz = self.env[req.create_analysis_wizard()['res_model']].with_context(
                        default_analysis_request=req.id)
                    w1 = wiz.create({
                        'analysis_request': req.id,
                    })
                    defaults = w1.default_get(w1._fields)
                    w1.write(defaults)
                    w1.create_analysis()

            tot = REQUEST_SIZES[POPULATE_SIZE]
            ct += 1
            if not ct % 100:
                _logger.info(f"Requests - analysis creation: {ct}/{tot}")


@tagged('lgk', 'lims')
class TestLimsBaseLimsMatrix(TransactionCase):
    """ The goal of this class is to test the lims.matrix model
    """

    @users('lims_demo')
    def test_01_lims_matrix_compute_methods(self):
        """ Test lims.matrix compute methods """
        matrixes = self.env['lims.matrix'].search([])
        for record in matrixes:
            count_nb_parameter_pack = self.env['lims.parameter.pack'].search_count([('matrix_id', '=', record.id)])
            count_nb_method_param_charac = self.env['lims.method.parameter.characteristic'].search_count(
                [('matrix_id', '=', record.id)])
            self.assertEqual(record.nb_parameter_pack, count_nb_parameter_pack)
            self.assertEqual(record.nb_method_param_charac, count_nb_method_param_charac)


@tagged('lgk', 'lims')
class TestLimsBaseLimsMethodParameterCharacteristic(TransactionCase):
    """ The goal of this class is to test the lims.method.parameter.characteristic model
    """

    @users('lims_demo')
    def test_01_lims_method_parameter_characteristic(self):
        """ Test lims.method.parameter.characteristic compute methods """
        params = self.env['lims.method.parameter.characteristic'].search([])
        for record in params:
            parameter_pack_count = record.env['lims.parameter.pack'].search_count(
                [('parameter_ids.method_param_charac_id', '=', record.id)])
            self.assertEqual(record.parameter_pack_count, parameter_pack_count)

