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
from odoo import models, fields, api, exceptions, _


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    reception_temperature = fields.Char()

    def do_todo(self):
        if self.filtered(lambda r: not r.date_sample_receipt):
            raise exceptions.ValidationError(
                _('You can not pass the analysis in todo if there is no date sample receipt'))
        return super(LimsAnalysis, self).do_todo()

    @api.onchange('sampling_point_id')
    def onchange_sampling_point_id(self):
        res = super(LimsAnalysis, self).onchange_sampling_point_id()
        if self.sampling_point_id:
            self.category_id = self.sampling_point_id.analysis_category_id
            self.regulation_id = self.sampling_point_id.regulation_id
        return res

    @api.model
    def create(self, vals):
        if vals.get('sampling_point_id') and (not vals.get('category_id') or not vals.get('regulation_id')):
            sampling_point_id = self.env['lims.sampling.point'].browse(vals.get('sampling_point_id'))
            if not vals.get('category_id'):
                vals.update({
                    'category_id': sampling_point_id.analysis_category_id.id,
                })
            if not vals.get('regulation_id'):
                vals.update({
                    'regulation_id': sampling_point_id.regulation_id.id,
                })
        return super(LimsAnalysis, self).create(vals)

    def write(self, vals):
        if vals.get('sampling_point_id') and (not vals.get('category_id') or not vals.get('regulation_id')):
            sampling_point_id = self.env['lims.sampling.point'].browse(vals.get('sampling_point_id'))
            if not vals.get('category_id'):
                vals.update({
                    'category_id': sampling_point_id.analysis_category_id.id,
                })
            if not vals.get('regulation_id'):
                vals.update({
                    'regulation_id': sampling_point_id.regulation_id.id,
                })
        return super(LimsAnalysis, self).write(vals)
