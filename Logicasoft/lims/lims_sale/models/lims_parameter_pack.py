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
from odoo import models, fields


class LimsParameterPack(models.Model):
    _inherit = 'lims.parameter.pack'

    billable = fields.Boolean(tracking=True, help='Defines whether when generating a sell order, '
                                                  'this parameter group will generate an item line.')
    is_additional_invoiced = fields.Boolean(tracking=True,
                                           help='Allows parameter packs to be invoiced without generating the results '
                                                'in the analysis.')
    sale_price = fields.Float('Sale Price', related='product_id.list_price', readonly=True,
                              help="This is the sale price of the product.")
    so_section_name = fields.Char('Section name', translate=True,
                                  help="Define text for the SO's section,\n "
                                       "if empty the section will take the name of this group for this article.")
    working_day = fields.Integer(help="""
    Number of working days for this service,
    When generating a quote, the longest number of working days found for the packs in the request will be indicated.
    (Ignore configuration of 0 days)
    """)
    allow_additional_pack_invoiced = fields.Boolean(compute='get_allow_additional_pack_invoiced', compute_sudo=True)

    def get_product(self, sample_id=False, analysis_id=False):
        """
        Return product that will be used to compute analysis costing and SO
        :return: (product.product)
        """
        self.ensure_one()
        return self.product_id

    def get_field_to_test(self):
        """
        Bypass Validation control, if pack is in state 'validated'
        :return:
        """
        res = super(LimsParameterPack, self).get_field_to_test()
        res += [u'billable', u'so_section_name', u'business_day', 'allow_additional_pack_invoiced']
        return res

    def get_is_additional_invoiced(self):
        """
        Used to
        :return:
        """
        self.ensure_one()
        return self.get_allow_additional_pack_invoiced() and self.is_additional_invoiced

    def get_allow_additional_pack_invoiced(self):
        config = bool(self.env['ir.config_parameter'].sudo().get_param('lims_sale.additional_pack_invoiced', False))
        # Method is called in get_is_additional_invoiced, so compute_sudo alone doesn't work
        # FIXME: I'm pretty sure there's a better way to to this (not a fan on the obligation to add sudo() inside
        #  the method) => should be reanalysed
        for record in self.sudo():
            record.allow_additional_pack_invoiced = config
        return config
