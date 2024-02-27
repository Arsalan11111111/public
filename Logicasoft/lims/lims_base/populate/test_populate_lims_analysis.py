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
from itertools import groupby, chain, islice
from functools import reduce
from collections import defaultdict
from operator import itemgetter
from odoo import fields, models, api, exceptions, SUPERUSER_ID, registry, Command
from odoo.tools import populate, convert_file
from odoo.tests.common import TransactionCase, tagged, users, Form
from odoo.modules import get_manifest
from .common import POPULATE_SIZE, REQUEST_SIZES


_logger = logging.getLogger(__name__)


def log_progress(it, qualifier='elements', logger=_logger, size=None):
    if size is None:
        size = len(it)
    size = float(size)
    t0 = t1 = datetime.datetime.now()
    for i, e in enumerate(it, 1):
        yield e
        t2 = datetime.datetime.now()
        if (t2 - t1).total_seconds() > 60:
            t1 = datetime.datetime.now()
            tdiff = t2 - t0
            logger.info("[%.02f%%] %d/%d %s processed in %s (TOTAL estimated time: %s)",
                        (i / size * 100.0), i, size, qualifier, tdiff,
                        datetime.timedelta(seconds=tdiff.total_seconds() * size / i))


def group_by(seq, key):
    res = reduce(
        lambda grp, val: grp[key(val)].append(val[1]) or grp, seq, defaultdict(list)
    )
    return dict(res)


class LimsAnalysisRequest(models.Model):
    _inherit = "lims.analysis.request"
    _populate_sizes = REQUEST_SIZES
    _populate_dependencies = ["lims.request.product.pack"]

    def _populate_factories(self):
        laboratory = self.env.ref('lims_base.default_laboratory')
        customer_1 = self.env.ref("lims_base.demo_lims_partner_4")
        customer_2 = self.env.ref("lims_base.demo_lims_partner_5")

        return [
            ("labo_id", populate.constant(laboratory.id)),
            ("partner_id", populate.randomize([customer_1.id, customer_2.id])),
        ]

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
            num_pack = random.randint(1, 3)
            for _ in range(num_pack):
                assign_pack(req, pack_ids_pool, param_pack_line)

    def _populate(self, size):
        records = super()._populate(size)
        packs = self.env['lims.request.product.pack'].search([])
        param_pack_line = self.env['lims.parameter.pack.line'].search([])
        self.assign_packs_to_requests(records, packs.ids, param_pack_line)

        for req in log_progress(records):
            if req.product_ids and (req.product_ids.pack_ids or req.product_ids.method_param_charac_ids):
                req.generate_request_sample_line()
                if random.randint(0, 9) <= 6:
                    req.do_confirmed()

                if req.state == 'accepted' and random.randint(0, 9) <= 7:
                    # generate analysis
                    wiz = self.env[req.create_analysis_wizard()['res_model']].with_context(
                        default_analysis_request=req.id)
                    w1 = wiz.create({
                        'analysis_request': req.id,
                    })
                    defaults = w1.default_get(w1._fields)
                    w1.write(defaults)
                    w1.create_analysis()

        return records


class LimsRequestProductPack(models.Model):
    _inherit = "lims.request.product.pack"
    # normally: triple the sizes of the requests should be enough:
    _populate_sizes = {k: v*3 for k, v in REQUEST_SIZES.items()}
    _populate_dependencies = ["lims.matrix"]

    def _populate(self, size):
        records = super()._populate(size)
        packs = self.env['lims.parameter.pack'].search([])
        packs_by_matrix_id = group_by([(p.matrix_id.id, p) for p in packs], itemgetter(0))

        for rec in records:
            available_packs = packs_by_matrix_id.get(rec.matrix_id.id)
            for _ in range(random.randint(0, 5)):
                pack = random.choice(available_packs)
                rec.pack_ids = [(6, 0, [pack.id])]

        return records

    def _populate_factories(self):
        matrix_ids = self.env['lims.matrix'].search([]).mapped('id')
        return [
            ("matrix_id", populate.randomize(matrix_ids)),
        ]


class InitLimsTestData(models.Model):
    """This is a false class and model. The purpose is to create test data when demo data has not been installed
    """
    _inherit = "lims.matrix"
    _populate_sizes = {"small": 1, "medium": 1, "large": 1}

    def _populate(self, size):
        existing = self.env['lims.matrix'].search([])
        enterprise = self.env['ir.config_parameter'].search([('key', '=', 'database.enterprise_code')])
        if existing or enterprise:
            # we don't create them again if they are already there
            # and we don't create them in a production database
            return existing

        demo_files = get_manifest('lims_base').get('demo', [])
        for demo_file in demo_files:
            convert_file(self.env.cr, 'lims_base', demo_file, {}, mode='init', noupdate=False, kind='data')

        return self.env['lims.matrix'].search([])

