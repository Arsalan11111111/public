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
from odoo import fields, models, api, _, exceptions
from odoo.tools.float_utils import float_round


class LimsAnalysisRequestSample(models.Model):
    _name = 'lims.analysis.request.sample'
    _order = 'rel_sequence, sequence, id'
    _description = 'Analysis Request Sample'

    sequence = fields.Integer(default=1)
    request_id = fields.Many2one('lims.analysis.request', string='Request', required=True, index=True)
    name = fields.Char('Name', index=True)
    matrix_type_id = fields.Many2one('lims.matrix.type', string='Matrix Type')
    matrix_id = fields.Many2one('lims.matrix', string='Matrix', required=True, index=True)
    auto = fields.Boolean('Auto', readonly=1, default=False)
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', index=True, help="The analysis that will create "
                                                                                "the results with that samples.")
    rel_parent_analysis_id = fields.Many2one('lims.analysis', related='analysis_id.parent_id',
                                             help="The parent analysis of the analysis linked with the samples.")
    product_pack_id = fields.Many2one('lims.request.product.pack', 'product', ondelete='cascade')
    pack_ids = fields.Many2many('lims.parameter.pack', string='Packs', readonly=1, context={'active_test': False})
    regulation_id = fields.Many2one('lims.regulation', 'Regulation')
    date_plan = fields.Datetime('Date Plan', index=True)
    combined = fields.Boolean('Combined')
    dilution_factor = fields.Float('Dilution Factor', default=1,
                                   help="If you change the dilution factor it will be change also on the analysis.")
    color = fields.Char('Color', compute='get_color_and_location', store=True, readonly=False,
                        help="It's equal to the 'Color' of the product that have created that sample.")
    location = fields.Char(compute='get_color_and_location', store=True, readonly=False, string='Location*',
                           help="It's equal to the 'Location' of the product that have created that sample.")
    comment = fields.Char()
    state = fields.Char(compute='compute_state', store=True, index=True,
                        help="It's equal to the 'State' of the analysis linked to that samples.")
    rel_analysis_stage_id = fields.Many2one(related='analysis_id.stage_id',
                                            help="It's equal to the 'Stage' of the analysis linked to that samples.")
    method_param_charac_ids = fields.Many2many('lims.method.parameter.characteristic',
                                               'rel_request_sample_method_param', 'request_sample_id',
                                               'method_param_charac_id', string='Parameters', readonly=1,
                                               context={'active_test': False})
    pack_of_pack_ids = fields.Many2many('lims.parameter.pack', 'rel_request_sample_pack_of_packs', 'request_sample_id',
                                        'pack_id', string='Pack of packs', readonly=1)
    rel_sequence = fields.Integer(related='product_pack_id.sequence', store=True, string="sequence",
                                  help="It's equal to the 'Sequence' of the product that have created that sample.")
    product_id = fields.Many2one('product.product', 'Product')

    def unlink(self):
        if self.filtered(lambda r: r.analysis_id):
            raise exceptions.ValidationError('Please delete the analysis before delete the line')
        return super(LimsAnalysisRequestSample, self).unlink()

    @api.depends('analysis_id', 'analysis_id.state')
    def compute_state(self):
        """
        Set the state of the sample (the same than the analysis)
        :return:
        """
        for record in self:
            record.state = record.analysis_id.state

    @api.depends('product_pack_id.color', 'product_pack_id.location')
    def get_color_and_location(self):
        """
        Set the color and location depends on the product_pack
        :return:
        """
        for record in self.filtered(lambda r: r.product_pack_id):
            record.color = record.product_pack_id.color
            record.location = record.product_pack_id.location

    def write(self, vals):
        """
        Write on the record, Set the dilution factor in analysis when write on it
        :param vals:
        :return:
        """
        res = super(LimsAnalysisRequestSample, self).write(vals)
        if vals.get('dilution_factor'):
            for record in self:
                record.onchange_dilution_factor_analysis()
        if self.analysis_id and vals.get('name') and not self.env.context.get('force_write'):
            self.mapped('analysis_id').with_context(force_write=True).write({'sample_name': vals.get('name')})
        return res

    @api.onchange('dilution_factor', 'analysis_id')
    def onchange_dilution_factor_analysis(self):
        """
        Check if dilution factor is 0 < X =< dilution factor max present in the laboratory, set in analysis the dilution
         factor
        :return:
        """
        self.ensure_one()
        # Avoid residuals problems for decimal.
        digits = self.env['decimal.precision'].precision_get('Analysis Result') + 2
        dilution_max = float_round(self.request_id.labo_id.dilution_factor_max, precision_digits=digits)
        dilution_factor = float_round(self.dilution_factor, precision_digits=digits)
        if not (0 < dilution_factor <= dilution_max):
            raise exceptions.ValidationError(
                _('Factor could not be below / equal 0 or greater than {}, '
                  'as defined in the Lab configuration.').format(dilution_max))
        if self.analysis_id:
            self.analysis_id.dilution_factor = self.dilution_factor

    def add_parameters(self):
        """
        Open the wizard for add parameter
        :return:
        """
        self.ensure_one()
        return {
            'name': _('Add parameters'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.parameters.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_sample_id': self.id}
        }


    def open_view_element(self):
        """
        Open element in form (like wizard view) in other elements.
        :return:
        """
        return {
            'name': _('View Form'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'origin_request': True}
        }

    def get_regulation(self):
        return self.analysis_id.regulation_id.ids or self.regulation_id.ids

    def get_sample_packs_and_pack_of_packs(self):
        packs = self.env['lims.parameter.pack']
        for record in self:
            packs += (record.analysis_id and record.analysis_id.get_analysis_packs_and_pack_of_packs()) or (
                        record.pack_ids + record.pack_of_pack_ids)
        return packs
