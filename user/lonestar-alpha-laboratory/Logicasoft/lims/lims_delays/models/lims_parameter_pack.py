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
from odoo import fields, models, api


class LimsParameterPack(models.Model):
    _inherit = 'lims.parameter.pack'

    commercial_lead_time = fields.Float(string='Commercial lead time',
                                        help='Define a commercial lead time (in hour(s)) for this pack; for an '
                                             'analysis that includes several pack, the highest lead time value will '
                                             'be applied to the all set of results. If this field is empty then no '
                                             'time will be calculated.')
    commercial_warning_time = fields.Float(string='Commercial warning time',
                                           help='Define a commercial warning time (in hour(s)) for this pack; for an '
                                                'analysis that includes several pack, it\'s the warning time from the '
                                                'highest commercial lead time value that will be applied to the all '
                                                'set of results. If this field is empty then no commercial warning '
                                                'time will be calculated.')

    @api.onchange('labo_id')
    def on_change_labo_id(self):
        if self.labo_id:
            self.commercial_lead_time = self.labo_id.default_commercial_lead_time
            self.commercial_warning_time = self.labo_id.default_commercial_warning_time
