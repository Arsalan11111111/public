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
from odoo import fields, api, models


class ContainerReportParser(models.AbstractModel):
    _name = 'report.lims_base.container_report_parser'
    _template = 'lims_base.container_report_parser'
    _description = 'Container Report Parser'

    def get_containers_ids(self, analysis_ids):
        container_ids = {}
        for analyse in analysis_ids:
            containers_by_analysis = {}
            for sop in analyse.sop_ids.filtered(lambda s: s.rel_type != 'cancel'):
                for container in sop.method_id.container_ids:
                    if container.product_id.id not in containers_by_analysis:
                        containers_by_analysis[container.product_id.id] = {'name': container.product_id.name,
                                                                           'qty': container.qty,
                                                                           'uom': container.uom.name}
                    elif containers_by_analysis[container.product_id.id]['qty'] < container.qty:
                        containers_by_analysis[container.product_id.id]['qty'] = container.qty
            for container in containers_by_analysis:
                if container_ids.get(container):
                    qty = containers_by_analysis[container]['qty']
                    container_qty = container_ids[container]['qty']
                    container_ids[container].update({
                        'qty': qty + container_qty
                    })
                else:
                    container_ids.update({
                        container: containers_by_analysis[container]
                    })
        return container_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'lims.analysis',
            'docs': self.env['lims.analysis'].browse(docids),
            'data': data,
            'get_containers_ids': self.get_containers_ids,
        }
