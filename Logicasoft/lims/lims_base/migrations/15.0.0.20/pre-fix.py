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
    # remove obsolete view
    cr.execute("""\
      WITH del AS
        (DELETE
         FROM ir_ui_view
         WHERE id in
             (SELECT v.id
              FROM ir_ui_view v
                 , ir_model_data d
              WHERE d.model = 'ir.ui.view'
                AND d.res_id = v.id
                AND (d.module = 'lims_base')
                AND (d.name = 'external_layout_clean') ) RETURNING id)
      DELETE
      FROM ir_model_data USING del
      WHERE model = 'ir.ui.view'
        AND del.id = ir_model_data.res_id RETURNING *
    """)

    # new ir.config_parameter:
    # this is to avoid a duplicate key error
    # Don't run for lims v16 or +
    if int(version.split('.')[0]) < 16:
        cr.execute("""\
          SELECT p.id
               , d.module
          FROM ir_config_parameter p
          LEFT OUTER JOIN ir_model_data d ON d.model = 'ir.config_parameter'
          AND d.res_id = p.id
          WHERE p.key = 'is_advanced_parameter_selector'
        """)
        res = cr.fetchone()
        if res and res[1] != 'lims_base':
            cr.execute("""\
              INSERT INTO ir_model_data (
                create_uid, create_date, noupdate, name, MODULE,
                model, res_id
              ) VALUES (
                1, now() AT TIME ZONE 'UTC', 't', 'is_advanced_parameter_selector', 'lims_base',
                'ir.config_parameter', %s)
            """,
            [res[0]])

    # delete obsolete selection:
    cr.execute("""\
      WITH del AS
        (DELETE
         FROM ir_model_fields_selection
         WHERE id in
             (SELECT s.id
              FROM ir_model_fields_selection s
                 , ir_model_fields f
                 , ir_model_data d
              WHERE d.model = 'ir.model.fields.selection'
                AND d.res_id = s.id
                AND f.id = s.field_id
                AND (d.module = 'lims_base')
                AND (f.model in (
                  'lims.analysis.notification.result.state',
                  'lims.analysis.notification'
                )) ) RETURNING id)
      DELETE
      FROM ir_model_data USING del
      WHERE model = 'ir.model.fields.selection'
        AND del.id = ir_model_data.res_id RETURNING *
    """)

    cr.execute("""\
      WITH del AS
        (DELETE
         FROM ir_cron
         WHERE id in
             (SELECT c.id
              FROM ir_cron c
                 , ir_act_server s
                 , ir_model_data d
              WHERE d.model = 'ir.cron'
                AND d.res_id = c.id
                AND c.ir_actions_server_id = s.id
                AND (d.module = 'lims_base')
                AND (s.model_name in (
                  'lims.analysis.notification.result.state',
                  'lims.analysis.notification.history',
                  'lims.analysis.notification'
                )) ) RETURNING id)
      DELETE
      FROM ir_model_data USING del
      WHERE model = 'ir.model'
        AND del.id = ir_model_data.res_id RETURNING *
    """)

    cr.execute("""\
      WITH del AS
        (DELETE
         FROM ir_model
         WHERE id in
             (SELECT m.id
              FROM ir_model m
                 , ir_model_data d
              WHERE d.model = 'ir.model'
                AND d.res_id = m.id
                AND (d.module = 'lims_base')
                AND (m.model in (
                  'lims.analysis.notification.result.state',
                  'lims.analysis.notification.history',
                  'lims.analysis.notification'
                )) ) RETURNING id)
      DELETE
      FROM ir_model_data USING del
      WHERE model = 'ir.model'
        AND del.id = ir_model_data.res_id RETURNING *
    """)




