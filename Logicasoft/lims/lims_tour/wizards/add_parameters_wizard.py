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
from odoo import models, fields, api


class AddParametersWizard(models.TransientModel):
    _inherit = 'add.parameters.wizard'

    def get_tour_line(self):
        tour_line_id = False
        if self.env.context.get('default_tour_line_id'):
            tour_line_id = self.env['lims.tour.line'].browse(self.env.context.get('default_tour_line_id'))
        return tour_line_id

    tour_line_id = fields.Many2one('lims.tour.line', default=get_tour_line)

    def create_results(self):
        res = super(AddParametersWizard, self).create_results()
        if self.tour_line_id:
            self.tour_line_id.color_on_line = True
        if self.analysis_id and self.analysis_id.tour_id and self.analysis_id.result_num_ids.filtered(lambda r: not r.tour_id):
            self.analysis_id.result_num_ids.filtered(lambda r: not r.tour_id).write({'tour_id': self.analysis_id.tour_id.id})
        return res
