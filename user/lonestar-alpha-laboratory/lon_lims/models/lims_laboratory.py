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
from odoo import fields, models, _


class LimsLaboratory(models.Model):
    _inherit = 'lims.laboratory'

    def get_default_note_report(self):
        return _("""
        <div style="text-align: center; font-weight: bold">TERMS &amp; CONDITIONS</div>
        Lonestar Alpha Laboratories conducts testing, analysis and reporting of samples in accordance with its Quality Management System, subject to the following terms and conditions.
        <ul style="list-style-type: decimal">
            <li>
                Lonestar Alpha shall follow internationally accepted methodologies for performing analysis/testing. In case the customer does not specify the test method to be used, Lonestar Alpha has the freedom to adopt any National/International standard Specification for conducting the requested tests. If a standard specification is un-available, Lonestar Alpha shall follow a Standard Operating Procedure (SOP) developed by Lonestar Alpha Laboratories.
            </li>
            <li>
                The results reported by Lonestar Alpha are only for the sample(s) analyzed/tested. No conclusion shall be drawn as to the applicability of the results to the entire sample population unless sampling was conducted in accordance with internationally accepted statistical sampling protocols.
            </li>
            <li>
                Testing and reporting pertain to the sample(s) tested and does not constituteendorsement of the product by Lonestar Alpha.
            </li>
            <li>
                The  test  report  issued  by  Lonestar  Alpha  contains  sample  identification  as  provided  by  the customer.  Lonestar  Alpha  dose  not  independently  verify  the  authenticity  of  the  sample identification, unless Lonestar Alpha technicians(s) are involved in the sampling.
            </li>
            <li>
                The test report shall not be produced in full or in part for any promotional or publicity purposes without the written consent of Lonestar Alpha.
            </li>
            <li>
                Under no circumstances Lonestar Alpha accepts any liability for loss or damage; consequential or otherwise, caused by use or misuse of the results. Lonestar Alpha liability is strictly limited to the testing fee charged for the sample in question, in case of proven negligence by Lonestar Alpha.
            </li>
            <li>
                In  case  of  cancellation  of  order  by  the  customer  for  any  reason,  all  costs  incurred  including incidental expenses, if any, shall be charged to the customer.
            </li>
            <li>
                Data/ information supplied by customer or any deviations in the sampling by customer /deviations in the specified environmental conditions could affect the validity of the results.
            </li>
            <li>
                Until or unless requested by customer laboratory does not specify statement of conformity/decision rule on the test reports.
            </li>
            <li>
                Sample storage retention time is as per laboratory procedure, any extra retention time shall be based upon interested customer request only and similarly additional cost shall apply.
            </li>
            <li>
                Both Laboratory and involved parties are responsible, through legally enforceable commitments such as contracts, agreements or work orders and related communication with customer for the management of all information obtained or created during the performance of laboratory services.
            </li>
            <li>
                The  laboratory  and  any  other  parties  involved  in  this  activity  shall  be  responsible  for confidentiality/impartiality information. The recipient of confidential information shall not release or disclose, without the instruction or prior laboratory permission
            </li>
        </ul>
        """)

    def get_default_note_report_validated(self):
        return _("For and on behalf of Lonestar Alpha Laboratories")

    note_report = fields.Html(default=get_default_note_report)
    note_report_validated = fields.Html(default=get_default_note_report_validated)
