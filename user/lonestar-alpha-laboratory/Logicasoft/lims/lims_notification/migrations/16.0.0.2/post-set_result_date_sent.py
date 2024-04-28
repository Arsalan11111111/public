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
def migrate(cr, version):
    """
    Set date_notification_sent on results to the first mails to send all the results
    """
    cr.execute("""
        SELECT lastcall FROM ir_cron WHERE ir_actions_server_id = (
        SELECT id FROM ir_act_server WHERE model_name='lims.analysis.notification' ORDER BY id LIMIT 1);
    """)
    lastcall = cr.fetchone()
    if lastcall:
        results_tables = ['lims_analysis_numeric_result', 'lims_analysis_sel_result', 'lims_analysis_text_result',
                          'lims_analysis_compute_result']
        result_query = "UPDATE {table} SET date_notification_sent = '{lastcall}' WHERE create_date < '{lastcall}'"
        for result_table in results_tables:
            cr.execute(result_query.format(table=result_table, lastcall=lastcall[0]))
        cr.execute(f"UPDATE lims_analysis_notification SET last_sent_date = '{lastcall[0]}'")
