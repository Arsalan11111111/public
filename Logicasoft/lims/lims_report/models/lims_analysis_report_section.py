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
from odoo.tools import html2plaintext


class LimsAnalysisReportSection(models.Model):
    _name = 'lims.analysis.report.section'
    _description = 'Report Section'
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
    name = fields.Char(required=True)
    print_name = fields.Char('Print Name', translate=True)
    introduction_text = fields.Html(string='Introduction text', translate=True,
                                    help="This text will be printed just before the parameter print groups.")
    conclusion_text = fields.Html(string='Conclusion text', translate=True,
                                  help="This text will be printed just after the parameter print groups.")
    is_with_bottom_separator = fields.Boolean('With bottom separator', default=False)

    print_group_ids = fields.One2many('lims.parameter.print.group', 'section_id')

    def get_introduction_text(self):
        self.ensure_one()
        return self.introduction_text if bool(html2plaintext(self.introduction_text)) else False

    def get_conclusion_text(self):
        self.ensure_one()
        return self.conclusion_text if bool(html2plaintext(self.conclusion_text)) else False
