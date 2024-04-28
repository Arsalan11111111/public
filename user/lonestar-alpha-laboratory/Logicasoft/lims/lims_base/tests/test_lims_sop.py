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
import odoo.tests
from odoo.tests.common import TransactionCase, tagged, users, Form
from ..populate.common import CommitedTransactionCase, POPULATE_SIZE, REQUEST_SIZES


_logger = logging.getLogger(__name__)


@tagged('lgk', 'lims', 'populate')
class TestLimsBaseLimsSop(CommitedTransactionCase):
    """ The goal of this class is to test the lims.sop model
    """

    @users('lims_demo')
    def test_01_validate_sop(self):
        """ Test the validation of SOP (tests)"""

        lims_sop_records = self.env['lims.sop'].search([])
        plan_stages = self.env['lims.method.stage'].search([('type', '=', 'plan')])
        todo_stages = self.env['lims.method.stage'].search([('type', '=', 'todo')])
        wip_stages = self.env['lims.method.stage'].search([('type', '=', 'wip')])

        ct = 0
        for sop in lims_sop_records:
            if sop.stage_id in plan_stages:
                # keep a few sops as is:
                if random.randint(0, 9) <= 7:
                    # generate analysis
                    sop.do_todo()
                    self.assertTrue(sop.stage_id in todo_stages)
                    if random.randint(0, 9) <= 7:
                        if sop.display_info_subcontracted and not sop.has_sample:
                            sop.has_sample = True
                        sop.do_wip()
                        self.assertTrue(sop.stage_id in wip_stages)

            tot = len(lims_sop_records)
            ct += 1
            if not ct % 100:
                _logger.info(f"lims.sop - todo or wip: {ct}/{tot}")

    @users('lims_demo')
    def test_02_create_batch(self):
        """ Test the creation of Batch (of tests)"""

        todo_stages = self.env['lims.method.stage'].search([('type', '=', 'todo')])
        plan_stages = self.env['lims.method.stage'].search([('type', '=', 'plan')])

        demo_dep = self.env.ref('lims_base.demo_department_1')
        demo_lab = self.env.ref('lims_base.default_laboratory')
        lims_sop_records = self.env['lims.sop'].search([
            ('stage_id', 'in', todo_stages.ids),
            ('department_id', '=', demo_dep.id),
            ('labo_id', '=', demo_lab.id),
        ])

        # create batch for a 5th of the number of sops:
        tot = len(lims_sop_records)
        num_test_sample = int(tot / 5)
        test_sample = []
        for _ in range(num_test_sample):
            sop_index = random.randint(0, tot-1)
            sop_id = lims_sop_records.ids[sop_index]
            test_sample.append(sop_id)
        test_sample = list(set(test_sample))

        def do_create_batch(test_sample):
            # create batch of up to 10 tests:
            num = random.randint(1, 10)
            tests_in_batch = []
            for _ in range(num):
                if test_sample:
                    sop_id = test_sample.pop()
                    tests_in_batch.append(sop_id)
                else:
                    return
            else:
                sops = lims_sop_records.browse(tests_in_batch)
                wiz = self.env['create.batch.wizard']
                w1 = wiz.create({
                    'batch_id': False,
                    'sop_ids': sops.ids,
                })
                batch = w1.do_create_batch()['res_id']
                return batch

        while test_sample:
            if not do_create_batch(test_sample):
                break

