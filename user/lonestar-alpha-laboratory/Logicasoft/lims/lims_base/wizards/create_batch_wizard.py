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


class CreateBatchWizard(models.TransientModel):
    _name = 'create.batch.wizard'
    _description = 'Create Batch'

    batch_id = fields.Many2one('lims.batch', string="Batch")
    sop_ids = fields.Many2many('lims.sop')
    department_id = fields.Many2one('lims.department')
    laboratory_id = fields.Many2one('lims.laboratory')

    @api.model
    def default_get(self, fields_list):
        res = super(CreateBatchWizard, self).default_get(fields_list)
        sop_ids = self.env.context.get('active_ids')
        if sop_ids:
            sop_ids = self.env['lims.sop'].browse(sop_ids)
            if len(sop_ids.mapped('department_id')) > 1 or len(sop_ids.mapped('labo_id')) > 1:
                raise exceptions.ValidationError(_("You can only create batch for tests within the same departments and"
                                                   " laboratories"))
            res.update({
                'sop_ids': [(4, sop_id.id) for sop_id in sop_ids],
                'department_id': sop_ids[0].department_id.id,
                'laboratory_id': sop_ids[0].labo_id.id,
            })
        return res

    def do_create_batch(self):
        if self.sop_ids:
            sop_ids = self.sop_ids
        else:
            sop_ids = self.env['lims.sop'].browse(self.env.context.get('active_ids'))
        res = sop_ids.do_create_batch(batch=self.batch_id)
        return res
