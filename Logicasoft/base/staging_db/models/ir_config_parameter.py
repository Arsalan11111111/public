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

import uuid
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def _staging_db(self):
        if not self._get_param('database.enterprise_code'):
            expiration_date_str = self.get_param('database.expiration_date')
            expiration_date = datetime.strptime(expiration_date_str, DEFAULT_SERVER_DATETIME_FORMAT)
            now = fields.Datetime.now()
            now_plus_3_months = now + relativedelta(months=+3)

            diff = (expiration_date - now).days
            if diff <= 18:
                self.set_param(
                    'database.uuid',
                    str(uuid.uuid1())
                )
                self.set_param(
                    'database.secret',
                    str(uuid.uuid4())
                )
                self.set_param(
                    'database.create_date',
                    now
                )
                self.set_param(
                    'database.expiration_date',
                    now_plus_3_months
                )

