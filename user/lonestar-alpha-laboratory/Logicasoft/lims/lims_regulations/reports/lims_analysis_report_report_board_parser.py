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


class LimsAnalysisReportReportBoardParser(models.AbstractModel):
    _inherit = 'report.lims_report.analysis_report_board'

    def get_conclusions(self, analysis, result, conclusions):
        if result:
            regulation_id = result['regulation_id']
            # state : text for conformity (will be printed on report)
            state = result.get('state')
            # limit_state : technical selection name for conformity (used to perform checks in the function)
            limit_state = result.get('limit_state')
            if not conclusions.get(analysis):
                conclusions.update({
                    analysis: {regulation_id: state}
                })
            else:
                current_state = conclusions[analysis].get(regulation_id)
                if current_state:
                    if current_state != 'not_conform' and limit_state == 'not_conform':
                        conclusions[analysis][regulation_id] = state
                else:
                    conclusions[analysis].update({
                        regulation_id: state
                    })
        return conclusions

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(LimsAnalysisReportReportBoardParser, self)._get_report_values(docids, data)
        res.update({
            'get_conclusions': self.get_conclusions,
        })
        return res
