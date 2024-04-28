#-*- encoding: utf8 -*-

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

import logging
import odoo
import odoo.tools as tools
from odoo.tests.suite import OdooSuite
from odoo.tests.tag_selector import TagsSelector
from odoo.tests.loader import get_test_modules, unwrap_suite
import unittest
DISABLED_WARNINGS = []


class OdooWarningFilter(logging.Filter):
    def filter(self, rec):
        return not (rec.levelno == logging.WARNING and rec.msg in DISABLED_WARNINGS)


def setup_warning_disable():
    global DISABLED_WARNINGS

    with odoo.registry(odoo.tools.config['db_name']).cursor() as cr:
        cr.execute("select 1 from ir_model_data where model = 'ir.model' and name = 'model_ir_warning_disable'")
        count = cr.fetchone()
        if count:
            cr.execute("select name from ir_warning_disable where active = 't'")
            DISABLED_WARNINGS = [r[0] for r in cr.fetchall()]

        root_logger = logging.root
        root_logger.addFilter(OdooWarningFilter())
        for handler in root_logger.handlers:
            if OdooWarningFilter.__name__ not in [f.__class__.__name__ for f in handler.filters]:
                handler.addFilter(OdooWarningFilter())

        for logger in [root_logger, root_logger.getChild('odoo.modules.loading')]:
            if OdooWarningFilter.__name__ not in [f.__class__.__name__ for f in logger.filters]:
                logger.addFilter(OdooWarningFilter())


def make_suite(module_names, position='at_install'):
    config_tags = TagsSelector(tools.config['test_tags'])
    config_tags.include = {('lgk', None, None, None, None)}
    position_tag = TagsSelector(position)

    tests = (
        t
        for module_name in module_names
        for m in get_test_modules(module_name)
        for t in unwrap_suite(unittest.TestLoader().loadTestsFromModule(m))
        if position_tag.check(t) and config_tags.check(t)
    )
    return OdooSuite(sorted(tests, key=lambda t: t.test_sequence))


from odoo.tests import loader
loader.make_suite = make_suite
setup_warning_disable()

