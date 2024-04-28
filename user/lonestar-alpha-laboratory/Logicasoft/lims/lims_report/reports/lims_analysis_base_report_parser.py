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
from odoo import models, api, _
from odoo.tools import html2plaintext
from odoo.tools import format_datetime


class LimsAnalysisBaseReportParser(models.AbstractModel):
    """
    Base parser not linked to a report, but that other analysis report parsers inherit, to avoid code duplication for
    functions used by all the reports
    """
    _name = 'report.lims_report.lims_analysis_base_report_parser'
    _description = 'Base analysis report parser'

    def get_method_comments(self, method_ids):
        return any([method.comment for method in method_ids])

    def return_month(self):
        months = [_('January'), _('February'), _('March'), _('April'), _('May'), _('June'),
                  _('July'), _('August'), _('September'), _('October'), _('November'), _('December')]
        return months

    def get_month(self, month):
        lang = self.env.user.lang or self.env.context.get('lang')
        months = self.with_context(lang=lang).return_month()
        return months[int(month) - 1]

    def set_accreditation(self, all_accreditation, result):
        if result and result.get('accreditation_ids'):
            for accreditation_id in result.get('accreditation_ids').filtered(lambda a: a not in all_accreditation):
                all_accreditation.append(accreditation_id)
        return all_accreditation

    def set_all_comment(self, all_comment, comment):
        if comment not in all_comment:
            all_comment.append(comment)
        return all_comment

    def add_method(self, methods, result):
        method_id = result['method_id']
        if not self.is_empty_html_field(method_id.comment):
            methods.append(method_id)
        return methods

    def is_empty_html_field(self, html_field):
        return not html_field or not bool(html2plaintext(html_field))

    def set_legends_items(self, legend_items, item):
        if item not in legend_items:
            legend_items.append(item)
        return legend_items

    def get_lang(self, doc):
        """
        Lang is called multiple times on report (mostly to add context to translatable fields), which make changing the
        language logic of the report very hard. This function will be useful to change the way to choose the report
        language without having to make multiple xpath to change languages
        :param doc: lims.analysis.report
        :return: lang code of the document
        """
        return doc.partner_id.lang if doc.partner_id else self.env.lang

    def format_date(self, date, lang_code='', fmt='d MMMM YYYY'):
        """
            date: date object (not string)
            lang_code: lang code (ex: fr_BE)
            fmt: date format using the Babel syntax:
                 https://babel.pocoo.org/en/latest/dates.html
        """
        fmt_date = format_datetime(
            self.env,
            date.strftime('%Y-%m-%d'),
            dt_format=fmt,
            lang_code=lang_code)
        return fmt_date

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': self.env['lims.analysis.report'].browse(docids),
            'doc_model': 'lims.analysis.report',
            'data': data,
            'get_method_comments': self.get_method_comments,
            'get_month': self.get_month,
            'set_accreditation': self.set_accreditation,
            'set_all_comment': self.set_all_comment,
            'add_method': self.add_method,
            'is_empty_html_field': self.is_empty_html_field,
            'set_legends_items': self.set_legends_items,
            'get_lang': self.get_lang,
            'format_date': self.format_date,
            'display_name_in_footer': True,
            'total_page_layout_bold': True
        }

