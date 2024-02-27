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
{
    'name': 'Test Disable',
    'version': '16.0.0.2',
    'summary': 'Allow to disable some tests from failing',
    'description': """
Standard tests sometimes fail because your custom modules modify the workflow.
This module allow some tests to be disabled.

If, in your log file, you get an error like: ::

  ERROR dbname odoo.addons.account_invoice_extract.tests.test_invoice_extract: FAIL: TestInvoiceExtract.test_bank_account

And you'd like to disable the corresponding test, you can add a new 'ir.test.disable' record with: ::

  name="odoo.addons.account_invoice_extract.tests.test_invoice_extract.TestInvoiceExtract.test_bank_account"

That test will now appear as succeeded.

    """,
    'license': 'Other proprietary',
    'category': 'Tests',
    'author': 'LogicaSoft SPRL',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_warning_disable.xml',
    ],
    'css': [],
    'test': [],
    'installable': True,
}
