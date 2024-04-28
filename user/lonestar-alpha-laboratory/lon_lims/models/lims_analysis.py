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
from odoo import fields, models


class LimsAnalysis(models.Model):
    _inherit = 'lims.analysis'

    intercessor_farmer_id = fields.Many2one('res.partner', string='Intercessor/Farmer')
    sample_origin_id = fields.Many2one('res.country', string='Origin of Sample')
    vehicle_number = fields.Char(string="DEC or Vehicle Number")
    quantity_of_sample = fields.Char(string="Quantity of sample")
    sampling_brought_by = fields.Char(string="Sampling brought by")
    sampling_method = fields.Char(string="Sampling method")
    testing_done_by_id = fields.Many2one("hr.employee", string="Testing done by")
    results_reviewed_by_id = fields.Many2one("hr.employee", string="Results reviewed by")
    results_approved_by_id = fields.Many2one("hr.employee", string="Results approved by")
    testing_location = fields.Char(string="Testing location")
    test_method_deviation = fields.Char(string="Test method deviation")
    project_name_id = fields.Many2one('res.partner', string='Project name')
    rel_product_category_id = fields.Many2one(related="product_id.categ_id", string="Product category", store=True)
    id_sampled_by = fields.Char(string="Sampler ID")
