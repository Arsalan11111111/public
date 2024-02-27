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
    method usefull  for migration from lims <= V11 (or maybe v12)
    :param cr:
    :param version:
    :return:
    """
    with cr.savepoint():
        # ANALYSIS STAGE
        cr.execute("SELECT id,type FROM lims_analysis_stage;")
        stage_ids = cr.dictfetchall()
        for stage_id in stage_ids:
            cr.execute(f"SELECT id FROM ir_model_data WHERE model='lims.analysis.stage' AND module='lims_base' AND "
                       f"name='{stage_id.get('type')}_analysis_stage';")
            result_ana = cr.dictfetchall()
            if len(result_ana) < 1:
                cr.execute(f"INSERT INTO ir_model_data (res_id, model, module, name) VALUES ('{stage_id.get('id')}',"
                           f"'lims.analysis.stage','lims_base', '{stage_id.get('type')}_analysis_stage');")

        # RESULT STAGE
        cr.execute("SELECT id,type FROM lims_result_stage;")
        stage_ids = cr.dictfetchall()
        for stage_id in stage_ids:
            cr.execute(f"SELECT id FROM ir_model_data WHERE model='lims.result.stage' AND module='lims_base' AND "
                       f"name='{stage_id.get('type')}_result_stage';")
            result_res = cr.dictfetchall()
            if len(result_res) < 1:
                cr.execute(f"INSERT INTO ir_model_data (res_id, model, module, name) VALUES ('{stage_id.get('id')}',"
                       f"'lims.result.stage','lims_base', '{stage_id.get('type')}_result_stage');")

        # IR CONFIG PARAMETER
        key_ids = [
            ['method_draft_stage_default_config', 'is_method_draft_stage_default'],
            ['method_plan_stage_default_config', 'is_method_plan_stage_default'],
            ['method_todo_stage_default_config', 'is_method_todo_stage_default'],
            ['method_wip_stage_default_config', 'is_method_wip_stage_default'],
            ['method_done_stage_default_config', 'is_method_done_stage_default'],
            ['method_validated_stage_default_config', 'is_method_validated_stage_default'],
            ['method_draft_cancel_default_config', 'is_method_cancel_stage_default'],
            ['analysis_stage_default_config', 'analysis_stage_id'],
            ['sop_stage_default_config', 'sop_stage_id'],
            ['default_laboratory_config', 'default_laboratory_ids']
        ]
        for key_id in key_ids:
            cr.execute(f"SELECT id FROM ir_model_data WHERE module = 'lims_base' AND name = '{key_id[0]}'")
            config = cr.dictfetchall()
            if len(config) < 1:
                cr.execute("INSERT INTO ir_model_data (res_id, module, model, name) VALUES ((SELECT id FROM "
                           f"ir_config_parameter WHERE key = '{key_id[1]}'),'lims_base','ir.config_parameter', "
                           f"'{key_id[0]}');")
