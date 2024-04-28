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
from odoo import models, api


class SopReportParser(models.AbstractModel):
    _name = 'report.lims_base.sop_report_parser'
    _description = 'Test Report Parser'

    @api.model
    def get_nb_print(self, print_id, sop_lines):
        sop_line = sop_lines.get(str(print_id))
        return sop_line[1]

    @api.model
    def get_analysis_name(self, print_id, sop_lines):
        sop_line = sop_lines.get(str(print_id))
        return sop_line[0]

    @api.model
    def _get_report_values(self, docids, data=None):
        deactivate_container = self.env['ir.config_parameter'].sudo().get_param('deactivate.container.label', False)

        sop_obj = self.env['lims.sop']
        sop_lines = {}

        if data and data.get('ids'):
            sop_ids = sop_obj.browse(data.get('ids'))
            lines = data.get('lines', {})
            sop_lines = {str(line[0]): (line[1][0], line[1][1]) for line in lines}
        else:
            sop_ids = sop_obj.browse(docids)
            for sop_id in sop_ids:
                sop_lines.update({
                    str(sop_id.id): (sop_id.analysis_id.name, sop_id.labo_id.nb_print_sop_label)
                })

        return {
            'doc_ids': docids,
            'doc_model': 'lims.sop',
            'data': data,
            'sop_ids': sop_ids.filtered(lambda s: s.rel_type != 'cancel'),
            'deactivate_container': deactivate_container,
            'get_nb_print': self.get_nb_print,
            'get_analysis_name': self.get_analysis_name,
            'sop_lines': sop_lines,
        }
