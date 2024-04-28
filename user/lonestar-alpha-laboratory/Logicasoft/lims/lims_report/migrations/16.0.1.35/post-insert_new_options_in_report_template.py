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
    version_list = version.split('.')
    # Dev from 15.0.5.17 avoid to run migration script twice.
    # If >16.0.0.0 or >15.0.5.16
    if (int(version_list[0]) >= 16 or (int(version_list[0]) <= 15 and int(version_list[1]) == 0
                                       and int(version_list[2]) <= 5 and int(version_list[3]) <= 16)
    ):
        """
        Step 1 Update all reports 'lims'.
        Step 2 Select all reports templates
        Step 3 Select all options fields
        Step 4 Link all option into template
        """
        cr.execute("UPDATE lims_analysis_report set option_print_value=true, option_print_uom=true;")
        cr.execute("SELECT id from lims_analysis_report_template;")
        template_ids = cr.fetchall()
        cr.execute(
            """SELECT id from ir_model_fields
                    WHERE model='lims.analysis.report' and name in ('option_print_value', 'option_print_uom');""")
        field_ids = cr.fetchall()
        cr.execute("""
        SELECT ir_model_fields_id, lims_analysis_report_template_id from ir_model_fields_lims_analysis_report_template_rel;
        """)
        options = cr.fetchall()
        links = ""
        for template_id in template_ids:
            for field_id in field_ids:
                # Avoid insert error for duplicate (key, key) in table
                if (field_id[0], template_id[0]) not in options:
                    links += f"({field_id[0]},{template_id[0]}),"
        if links:
            links = links[:-1]
            cr.execute("""INSERT INTO ir_model_fields_lims_analysis_report_template_rel
                        (ir_model_fields_id, lims_analysis_report_template_id)
                        values {};""".format(links))
