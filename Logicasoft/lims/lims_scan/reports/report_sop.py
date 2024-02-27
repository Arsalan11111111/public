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
from odoo import models, fields, api, tools


class ReportSop(models.Model):
    _name = 'report.sop'
    _auto = False
    _description = 'Report test'

    sop_id = fields.Many2one('lims.sop', 'Test')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis')
    analysis_stage_id = fields.Many2one('lims.analysis.stage', 'Analysis stage')
    method_stage_type = fields.Selection('get_type_selection', 'Stage type')
    nb_label = fields.Integer('Nb of labels', copy=False)

    @api.model
    def get_type_selection(self):
        return self.env['lims.method.stage'].get_type_selection()

    def _select(self):
        select_query = """
            SELECT row_number() OVER(ORDER BY s.id) as id, 
            a.id as analysis_id, 
            s.id as sop_id,
            s.nb_label as nb_label,
            mstage.type as method_stage_type
        """
        return select_query

    def _from(self):
        from_query = """
            FROM lims_analysis a
            JOIN lims_sop s on a.id = s.analysis_id
            JOIN lims_method_stage mstage on mstage.id = s.stage_id
        """
        return from_query

    def _where(self):
        where_query = """"""
        return where_query

    def _group_by(self):
        groupby_query = """
            a.id, s.id, mstage.id
        """
        return groupby_query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                %s
                %s
                %s
                GROUP BY %s
                
            )""" % (
            self._table, self._select(), self._from(), self._where(), self._group_by()))
