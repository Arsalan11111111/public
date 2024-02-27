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

from textwrap import dedent


def module_is_installed(cr, module_name):
    cr.execute(
        """
            SELECT 1 FROM ir_module_module WHERE state NOT IN ('uninstalled', 'uninstallable') AND name = %s
        """, [module_name]
    )
    return cr.fetchone()


def product_template_to_variant_in_parameter_char_product(cr, v13_or_more):
    cr.execute("""
        ALTER TABLE lims_parameter_char_product ADD COLUMN IF NOT EXISTS pcp_origin integer;
        ALTER TABLE lims_parameter_char_product DROP CONSTRAINT IF EXISTS lims_parameter_char_product_product_id_fkey;
        ALTER TABLE lims_method_parameter_characteristic_limit_product ADD COLUMN IF NOT EXISTS mpclp_origin integer;

        ALTER TABLE lims_method_parameter_characteristic_limit_product drop CONSTRAINT IF EXISTS "lims_method_parameter_characteri_parameter_char_product_id_fkey";
        ALTER TABLE lims_parameter_char_product drop constraint IF EXISTS "lims_parameter_char_product_method_param_charac_id_fkey";

        ALTER TABLE IF EXISTS lims_accreditation_lims_parameter_char_product_rel DROP CONSTRAINT IF EXISTS "lims_accreditation_lims_param_lims_parameter_char_product__fkey";
        ALTER TABLE IF EXISTS mass_duplicate_product_limit_wizard_line DROP CONSTRAINT IF EXISTS "mass_duplicate_product_limit_wiz_parameter_char_product_id_fkey";

        ALTER TABLE lims_parameter_char_product DROP CONSTRAINT IF EXISTS "lims_parameter_char_product_create_uid_fkey";
        ALTER TABLE lims_parameter_char_product DROP CONSTRAINT IF EXISTS "lims_parameter_char_product_matrix_id_fkey";
        ALTER TABLE lims_parameter_char_product DROP CONSTRAINT IF EXISTS "lims_parameter_char_product_write_uid_fkey";
        ALTER TABLE lims_method_parameter_characteristic_limit_product DROP CONSTRAINT IF EXISTS "lims_method_parameter_characteristic_limit_prod_create_uid_fkey";
        ALTER TABLE lims_method_parameter_characteristic_limit_product DROP CONSTRAINT IF EXISTS "lims_method_parameter_characteristic_limit_produ_write_uid_fkey";
    """)

    lims_conditionnal_tests_is_installed = module_is_installed(cr, 'lims_conditionnal_tests')

    if lims_conditionnal_tests_is_installed:
        cr.execute("""\
            ALTER TABLE rel_pack_limit_product DROP CONSTRAINT IF EXISTS "rel_pack_limit_product_limit_id_fkey";
        """)

    lims_conditionnal_tests_part = """
    pack_limit_lines AS (
        SELECT new_lim.id, pack_lim.pack_id
        FROM new_lim
        LEFT JOIN rel_pack_limit_product pack_lim
        ON pack_lim.limit_id = new_lim.mpclp_origin
        WHERE pack_lim.limit_id IS NOT NULL
    ),
    new_pack_limit AS (
        INSERT INTO rel_pack_limit_product(limit_id, pack_id)
        SELECT pack_limit_lines.id, pack_limit_lines.pack_id
        FROM pack_limit_lines
    ),
    """ if lims_conditionnal_tests_is_installed else ""

    v13_part = """
        accreditation_lines AS (
        SELECT new_pcp.id as new_pcp_id, new_pcp.pcp_origin, accr.lims_accreditation_id
        FROM new_pcp
        LEFT JOIN lims_accreditation_lims_parameter_char_product_rel accr
        ON accr.lims_parameter_char_product_id = new_pcp.pcp_origin
        WHERE accr.lims_parameter_char_product_id IS NOT NULL
    ),
    new_accr AS (
        INSERT INTO lims_accreditation_lims_parameter_char_product_rel(
            lims_parameter_char_product_id, lims_accreditation_id)
        SELECT accr.new_pcp_id
             , accr.lims_accreditation_id
        FROM accreditation_lines AS accr
    ),
    """ if v13_or_more else ""

    cr.execute("""
    SELECT name FROM ir_model_fields
    WHERE model_id=(SELECT id FROM ir_model WHERE model='lims.parameter.char.product' LIMIT 1)
    AND store=true AND ttype NOT IN ('one2many', 'many2many', 'binary' ,'monetary') AND name NOT IN ('id', 'product_id')
    """)
    parameter_char_product_fields = [name[0] for name in cr.fetchall()]

    cr.execute("""
        SELECT name FROM ir_model_fields
        WHERE model_id=(SELECT id FROM ir_model WHERE model='lims.method.parameter.characteristic.limit.product' LIMIT 1)
        AND store=true AND ttype NOT IN ('one2many', 'many2many', 'binary', 'monetary') AND name NOT IN ('id', 'parameter_char_product_id')
        """)
    method_parameter_limit_product_fields = [name[0] for name in cr.fetchall()]

    cr.execute("""
        SELECT relation FROM ir_model_fields WHERE model='lims.parameter.char.product' AND name='product_id';
    """)
    result = cr.fetchall()
    if result and result[0] and 'product.template' == result[0][0]:
        template_id = "p.product_id"
    else:
        template_id = "(SELECT product_tmpl_id FROM product_product WHERE id = p.product_id)"
    # solution for bad migration from product_template to product_product

    query = dedent(f"""\
    WITH sel AS (
        SELECT p.id
             , variant.id AS variant_id
             , {', '.join(['p.'+name for name in parameter_char_product_fields])}
        FROM lims_parameter_char_product p
        LEFT JOIN product_product variant ON variant.product_tmpl_id = {template_id}
    ),
    new_pcp AS (
        INSERT INTO lims_parameter_char_product(
            pcp_origin
            , product_id
            , {', '.join(parameter_char_product_fields)})
                SELECT sel.id
                     , sel.variant_id
                     , {', '.join(['sel.'+name for name in parameter_char_product_fields])}
                FROM sel RETURNING *
    ),
    {v13_part}
    limit_lines AS (
        SELECT new_pcp.id AS parameter_char_product_id
             , new_pcp.pcp_origin
             , lim.id AS lim_id
             , {', '.join(['lim.'+name for name in method_parameter_limit_product_fields])}
        FROM new_pcp
        LEFT JOIN lims_method_parameter_characteristic_limit_product lim
            ON lim.parameter_char_product_id = new_pcp.pcp_origin
        WHERE lim.parameter_char_product_id IS NOT NULL
    ),
    new_lim AS (
        INSERT INTO lims_method_parameter_characteristic_limit_product(
            parameter_char_product_id
          , mpclp_origin
          , {', '.join(method_parameter_limit_product_fields)}
        )
        SELECT lim.parameter_char_product_id
             , lim.lim_id
             , {', '.join(['lim.'+name for name in method_parameter_limit_product_fields])}
        FROM limit_lines AS lim
        RETURNING *
    ),
    {lims_conditionnal_tests_part}
    deleted_mpclp AS (
        DELETE
        FROM lims_method_parameter_characteristic_limit_product
        WHERE EXISTS (
          SELECT 1
          FROM sel
          WHERE sel.id = lims_method_parameter_characteristic_limit_product.parameter_char_product_id
        )
    )
    DELETE
    FROM lims_parameter_char_product
    WHERE EXISTS (
      SELECT 1
      FROM sel
      WHERE sel.id = lims_parameter_char_product.id
    )
    ;
    """)
    cr.execute(query)

    cr.execute("""
        ALTER TABLE lims_parameter_char_product DROP COLUMN IF EXISTS pcp_origin;
        ALTER TABLE lims_method_parameter_characteristic_limit_product DROP COLUMN IF EXISTS mpclp_origin;
    """)

    if v13_or_more:
        cr.execute("""
            DELETE
            FROM lims_accreditation_lims_parameter_char_product_rel
            WHERE lims_parameter_char_product_id not in
                (SELECT id
                 FROM lims_parameter_char_product);
            ALTER TABLE ONLY lims_accreditation_lims_parameter_char_product_rel ADD CONSTRAINT lims_accreditation_lims_param_lims_parameter_char_product__fkey
            FOREIGN KEY (lims_parameter_char_product_id) REFERENCES lims_parameter_char_product(id) ON
            DELETE CASCADE;
        """)

    if lims_conditionnal_tests_is_installed:
        cr.execute("""
        DELETE
        FROM rel_pack_limit_product
        WHERE limit_id not in
            (SELECT id
             FROM lims_method_parameter_characteristic_limit_product);
        ALTER TABLE ONLY rel_pack_limit_product ADD CONSTRAINT rel_pack_limit_product_limit_id_fkey
        FOREIGN KEY (limit_id) REFERENCES lims_method_parameter_characteristic_limit_product(id) ON
        DELETE CASCADE;
    """)


def migrate(cr, version):
    # Version check because some fields like accreditation_ids have only been added in V13, and obviously the join on an
    # nonexistent table doesn't work very well
    v13_or_more = int(version[:2]) >= 13
    product_template_to_variant_in_parameter_char_product(cr, v13_or_more)

