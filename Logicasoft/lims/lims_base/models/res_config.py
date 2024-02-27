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
from odoo import fields, models, api, _
from ast import literal_eval

from odoo.addons.base.models.res_users import _jsonable
from odoo.exceptions import UserError
from odoo.http import request
import json
import time
import decorator


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    analysis_stage_id = fields.Many2one('lims.analysis.stage', 'Analysis Default Stage',
                                        help='Defines when generating the analysis which stage is by default.',
                                        config_parameter='analysis_stage_id')
    sop_stage_id = fields.Selection('get_sop_stage_selection', 'Test Default Stage',
                                    help='Defines when generating the test which stage is by default.',
                                    config_parameter='sop_stage_id')
    deactivate_container_for_label = fields.Boolean(help='If checked, allows the user to modify the number of labels '
                                                         'printed via the action print label on a sample.',
                                                    config_parameter='deactivate_container_for_label')
    module_lims_attachment = fields.Boolean(string='Manage attachment in analysis',
                                            help='Installs module lims attachment')
    module_sync_drag_drop_attach = fields.Boolean(string='Drag & Drop Multi Attachments in Form View',
                                                  help='Installs module Drag & Drop Multi Attachments')
    module_lims_double_validation = fields.Boolean('Separate validation of results and tests',
                                                   help='Installs module Lims double validation')
    time_between_check_identity = fields.Integer(string='Delay between each session validation',
                                                 help="Defines the time in seconds for 'secure' actions which require"
                                                      " session validation by password confirmation.",
                                                 config_parameter='time_between_check_identity',
                                                 default=600)
    is_automatic_customer_follower = fields.Boolean('Automatically add customers as followers in request and analysis',
                                                    help='Once people have been attached to the request and the '
                                                         'analysis, this allows emails to be sent directly. It is also'
                                                         ' necessary when using the portal',
                                                    config_parameter='is_automatic_customer_follower')
    module_lims_partner_limit = fields.Boolean('Insert partner limit in method parameter characteristic',
                                                   help='Installs module Lims partner limit')
    module_lims_product_limit = fields.Boolean('Insert product limit in method parameter characteristic',
                                                   help='Installs module Lims product limit')
    priority_limit = fields.Selection(selection=[('partner', 'Partner'), ('product', 'Product')],
                                      string='Priority limit', default='product',
                                      help='Define which limit is used in first when results are create',
                                      config_parameter='priority_limit')
    is_parameter_and_pack_protected = fields.Boolean('Parameter characteristics and Pack validated is protected',
            config_parameter='is_parameter_and_pack_protected', default=False,
            help='Enable protection of validated characteristic parameters and validated packs.')

    @api.model
    def get_sop_stage_selection(self):
        return self.env['lims.method.stage'].get_type_selection()


@decorator.decorator
def check_identity_lgk(fn, self):
    """
    Alter function of odoo base,
    Used to generate session validation requests for functions marked by the decorator. @check_identity_lgk

    For this to be functional, a boolean must be added in the configuration table, this one must respect the syntax:
    'ask_password_' + table_name + '_' + function_name
    In addition, it is possible to add a configuration to change the session validation delay,
     for this it is also necessary to respect a syntax:
    'ask_password_time' + table_name + '_' + function_name
    if there is an error we will fall back to the default value: 600 seconds
    """
    if not request:
        raise UserError(_("This method can only be accessed over HTTP"))

    param_ask_psw = "ask_password_{}_{}".format(self._table, fn.__name__)
    configuration = self.env['ir.config_parameter'].sudo().get_param(param_ask_psw, default='False')
    if configuration == 'True':
        try:
            configuration_time = abs(int(self.env['ir.config_parameter'].sudo().get_param('time_between_check_identity',
                                                                                          default=600)))
        except ValueError:
            configuration_time = 600

        if request.session.get('identity-check-last', 0) > time.time() - configuration_time:
            # update identity-check-last like github?
            return fn(self)

        w = self.sudo().env['res.users.identitycheck'].create({
            'request': json.dumps([
                {  # strip non-jsonable keys (e.g. mapped to recordsets like binary_field_real_user)
                    k: v for k, v in self.env.context.items()
                    if _jsonable(v)
                },
                self._name,
                self.ids,
                fn.__name__
            ])
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.users.identitycheck',
            'res_id': w.id,
            'name': _("Security Control"),
            'target': 'new',
            'views': [(False, 'form')],
        }
    else:
        return fn(self)
