#!/usr/bin/env python
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
# This module is developed by LogicaSoft SPRL
# Copyright (C) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import erppeek

SERVER = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''


def main():
    client = erppeek.Client(SERVER, DATABASE, USERNAME, PASSWORD)
    sale_order_line_obj = client.model('sale.order.line')
    request_obj = client.model('lims.analysis.request')
    line_ids = sale_order_line_obj.search([('request_id', '=', False), ('state', '!=', 'cancel')])
    for line_id in line_ids:
        line = sale_order_line_obj.browse(line_id)
        request = False
        if line.sample_id:
            request = request_obj.search([('sample_ids', '=', line.sample_id.id)])[0]
        elif len(line.order_id.analysis_request_ids) == 1:
            request = line.order_id.analysis_request_ids[0].id
        elif len(line.order_id.order_line) > 1:
            order_line_with_request = sale_order_line_obj.search([('order_id', '=', line.order_id.id), ('request_id', '!=', False)])
            request = sale_order_line_obj.browse(order_line_with_request)[0].request_id.id
        if request:
            line.write({'request_id': request})
            for invoice_line in line.invoice_lines:
                if not invoice_line.request_id:
                    invoice_line.write({'request_id': request})


if __name__ == "__main__":
    main()
