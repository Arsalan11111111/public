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
    query_column_name = """
        DO $$
        BEGIN
          IF EXISTS(SELECT *
            FROM information_schema.columns
            WHERE table_name='lims_method_parameter_characteristic_rel' and column_name='col_1')
          THEN
              ALTER TABLE lims_method_parameter_characteristic_rel RENAME COLUMN col_1 TO parameter_charac_id;
          END IF;
        END $$;
        
        DO $$
        BEGIN
          IF EXISTS(SELECT *
            FROM information_schema.columns
            WHERE table_name='lims_method_parameter_characteristic_rel' and column_name='col_2')
          THEN
              ALTER TABLE lims_method_parameter_characteristic_rel RENAME COLUMN col_2 TO conditional_parameter_charac_id;
          END IF;
        END $$;
    """
    cr.execute(query_column_name)

    query_constraint = """
        ALTER INDEX IF EXISTS lims_method_parameter_characteristic_rel_col_2_col_1_idx RENAME TO 
        lims_method_parameter_characteristic_rel_conditional_parameter_charac_id_parameter_charac_id_idx;
        ALTER TABLE IF EXISTS lims_method_parameter_characteristic_rel DROP CONSTRAINT lims_method_parameter_characteristic_rel_col_1_fkey;
        ALTER TABLE IF EXISTS lims_method_parameter_characteristic_rel ADD CONSTRAINT 
        "lims_method_parameter_characteristic_rel_parameter_charac_id_fkey" FOREIGN KEY (parameter_charac_id)
        REFERENCES lims_method_parameter_characteristic(id) ON DELETE CASCADE;
        ALTER TABLE IF EXISTS lims_method_parameter_characteristic_rel DROP CONSTRAINT lims_method_parameter_characteristic_rel_col_2_fkey;
        ALTER TABLE IF EXISTS lims_method_parameter_characteristic_rel ADD CONSTRAINT 
        "lims_method_parameter_characteristic_rel_conditional_parameter_charac_id_fkey" 
        FOREIGN KEY (conditional_parameter_charac_id) 
        REFERENCES lims_method_parameter_characteristic(id) ON DELETE CASCADE;
    """
    cr.execute(query_constraint)
