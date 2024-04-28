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


class LimsRequestProductPack(models.Model):
    _inherit = 'lims.request.product.pack'


    pack_invoiced_ids = fields.Many2many('lims.parameter.pack',
                                         'rel_request_product_pack_pack_invoiced', 'request_product_pack_id', 'pack_id',
                                         string='Packs invoiced',
                                         help='Pack that will only be invoiced, and not generate on the analyses; An '
                                              'analysis with this legislation must be generated to add the sales '
                                              'supplements',
                                         context={'active_test': False})
    allow_additional_pack_invoiced = fields.Boolean(compute='get_allow_additional_pack_invoiced')

    def get_pack_invoiced_ids(self, regulation_id=False):
        self.ensure_one()
        packs = self.pack_invoiced_ids.filtered(lambda p: p.state == 'validated' and not p.is_pack_of_pack)
        if regulation_id and packs:
            packs = self._regulation_filter(packs, regulation_id)
        return packs

    def get_pack_of_pack_invoiced_ids(self, regulation_id=False):
        self.ensure_one()
        pack_of_packs = self.pack_invoiced_ids.filtered(lambda p: p.state == 'validated' and p.is_pack_of_pack)
        if regulation_id and pack_of_packs:
            pack_of_packs = self._regulation_filter(pack_of_packs, regulation_id)
        return pack_of_packs

    def _regulation_filter(self, item_ids, regulation_id):
        self.ensure_one()
        # regulation_id in regulation_id : Support also the lims_regulations module.
        return item_ids.filtered(lambda p: p.regulation_id in regulation_id)

    def get_allow_additional_pack_invoiced(self):
        config = bool(self.env['ir.config_parameter'].sudo().get_param('lims_sale.additional_pack_invoiced', False))
        for record in self:
            record.allow_additional_pack_invoiced = config
        return config
