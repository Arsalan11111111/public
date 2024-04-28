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
def get_fields_to_update(cr):
    table_names = ('lims_analysis', 'lims_analysis_request', 'lims_analysis_request_sample',
                   'lims_history', 'lims_matrix', 'lims_method_container', 'lims_method',
                   'lims_parameter_pack', 'lims_parameter', 'lims_request_product_pack')
    query = """
    SELECT rel_kcu.table_name, kcu.table_name
    FROM information_schema.table_constraints tco
JOIN information_schema.key_column_usage kcu
          ON tco.constraint_schema = kcu.constraint_schema
          AND tco.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rco
          ON tco.constraint_schema = rco.constraint_schema
          AND tco.constraint_name = rco.constraint_name
JOIN information_schema.key_column_usage rel_kcu
          ON rco.unique_constraint_schema = rel_kcu.constraint_schema
          AND rco.unique_constraint_name = rel_kcu.constraint_name
          AND kcu.ordinal_position = rel_kcu.ordinal_position
WHERE tco.constraint_type = 'FOREIGN KEY'
    AND kcu.column_name = 'product_id'
    AND kcu.table_name in {tables};
    """.format(tables=table_names)
    cr.execute(query)
    return cr.fetchall()


def convert_template_to_product(cr, table_to_update):
    cr.execute("""alter table {table} drop constraint {table}_product_id_fkey;""".format(table=table_to_update))
    query = """
        WITH sel AS (
          SELECT
            pp.id as product_id,
            pt.id as template_id
          FROM
            product_product pp,
            product_template pt
          WHERE pp.product_tmpl_id = pt.id
        )
        UPDATE {table}
        SET product_id = sel.product_id
        FROM sel
        WHERE
          {table}.product_id = sel.template_id
        ;
        """.format(table=table_to_update)
    cr.execute(query)


def migrate(cr, version):
    """
    Most many2one linked to product.template have been linked to product.product instead
    (task 19544 / commit f3e5a84bae0fd21cfaabc08586833f01e7a8b3a3)
    To avoid loosing existing data and generating integrity error on postgres we change the ids on the concerned
    """
    fields_to_update = get_fields_to_update(cr)
    for field_to_update in fields_to_update:
        field_model = field_to_update[0]
        table_to_update = field_to_update[1]
        if field_model == 'product_template':
            convert_template_to_product(cr, table_to_update)
