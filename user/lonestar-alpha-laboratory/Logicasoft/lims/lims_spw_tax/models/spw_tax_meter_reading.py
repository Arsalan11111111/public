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
from odoo import models, fields, api, _, exceptions


class SpwTaxMeterReading(models.Model):
    _name = 'spw.tax.meter.reading'
    _description = 'Spw Tax Meter Reading model'

    meter_id = fields.Many2one('spw.tax.meter', 'Meter', required=True)
    rel_reference = fields.Char(related='meter_id.reference')
    campaign_id = fields.Many2one('spw.tax.campaign', 'Campaign')
    readingby_id = fields.Many2one('res.partner', 'Reading By')
    start_date = fields.Datetime('Start Date')
    start_index = fields.Float('Start Index')
    end_date = fields.Datetime('End Date')
    end_index = fields.Float('End Index')
    outflow = fields.Float('Outflow', compute='compute_outflow', store=True)

    @api.depends('start_date', 'start_index', 'end_date', 'end_index')
    def compute_outflow(self):
        for record in self:
            if record.end_date and record.start_date and record.end_index:
                end_date = record.end_date
                start_date = record.start_date
                delta = (end_date - start_date).total_seconds() / (3600 * 24)
                record.outflow = (record.end_index - record.start_index) / delta

    @api.constrains('meter_id')
    def check_meter_id(self):
        if self.campaign_id and self.meter_id:
            meter_ids = self.search_count([('meter_id', '=', self.meter_id.id),
                                           ('campaign_id', '=', self.campaign_id.id)])
            if meter_ids > 1:
                raise exceptions.ValidationError(_("You can't add the same meter twice"))
        return True
