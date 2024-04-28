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
from odoo.tools import html2plaintext


class LimsParameterPrintGroup(models.Model):
    _name = 'lims.parameter.print.group'
    _order = 'sequence, id'
    _description = 'Parameter Print Group'

    parameter_print_ids = fields.Many2many('lims.parameter.print',
                                           'parameter_print_group_relation',
                                           'parameter_group_id',
                                           'parameter_print_id',
                                           'Parameter Print',
                                           help="The parameters print that will be represented by this group.")
    name = fields.Char('Name', required=True, translate=True)
    print_name = fields.Char('Print name', translate=True, required=True,
                             help="The name that will be printed on reports for the linked parameters print.")
    sequence = fields.Integer('Sequence', default=5)
    is_print_title = fields.Boolean('Print title', default=True)
    is_with_bottom_separator = fields.Boolean('With bottom separator', default=False)
    version = fields.Integer('Version', default=1)
    active = fields.Boolean('Active', default=True)
    introduction_text = fields.Html(string='Introduction text', translate=True,
                                    help="This text will be printed just before the table of analysis result.")
    conclusion_text = fields.Html(string='Conclusion text', translate=True,
                                  help="This text will be printed just after the table of analysis result.")
    section_id = fields.Many2one('lims.analysis.report.section', string='Report Section',
                                 help="The section regroup this parameter print group with others.")

    def get_introduction_text(self):
        self.ensure_one()
        return self.introduction_text if bool(html2plaintext(self.introduction_text)) else False

    def get_conclusion_text(self):
        self.ensure_one()
        return self.conclusion_text if bool(html2plaintext(self.conclusion_text)) else False
