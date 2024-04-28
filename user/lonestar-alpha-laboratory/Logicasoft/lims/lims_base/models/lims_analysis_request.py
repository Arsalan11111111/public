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
from odoo import fields, models, api, _, exceptions
from odoo.tools import html2plaintext


class LimsAnalysisRequest(models.Model):
    _name = 'lims.analysis.request'
    _description = 'Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'request_date desc, id desc'

    def get_default_laboratory(self):
        """
        :return: record of lims.laboratory if there is one
        """
        labo_id = self.env.user.default_laboratory_id
        if not labo_id:
            labo_id = self.env['lims.laboratory'].search([('default_laboratory', '=', True)])
        return labo_id

    partner_id = fields.Many2one('res.partner', 'Customer', required=True, index=True, help="The client of the request.")
    name = fields.Char('Name', index=True, readonly=True, help="The name of the request.")
    partner_contact_ids = fields.Many2many('res.partner', string='Customer contacts', help="A list of contacts of the client.")
    request_type_id = fields.Many2one('lims.request.category', 'Request type', index=True, help="The category of the request.")
    user_id = fields.Many2one('res.users', 'Responsible', index=True, tracking=True)
    customer_ref = fields.Char('Customer reference')
    request_date = fields.Date('Request date', default=fields.Date.today, index=True, copy=False)
    order_date = fields.Date('Order date', readonly=True, index=True, copy=False,
                             help="This date is set to the day when the request go on state 'accepted'.")
    customer_order_ref = fields.Char('Customer order reference')
    description = fields.Char('Description')
    state = fields.Selection('get_request_state', default='draft', index=True, tracking=True)
    labo_id = fields.Many2one('lims.laboratory', string='Laboratory', index=True, required=True,
                              default=get_default_laboratory)
    rel_company_id = fields.Many2one('res.company', related='labo_id.company_id',
                                     help="This is the company of the laboratory.")
    sample_ids = fields.One2many('lims.analysis.request.sample', 'request_id', string='Sample list')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium (*)'), ('3', 'High (**)'), ('4', 'Highest (***)')],
                                default='1')
    tag_ids = fields.Many2many('lims.analysis.request.tags', string='Tags')
    active = fields.Boolean('Active', default=True)
    analysis_ids = fields.One2many('lims.analysis', 'request_id', 'Analysis')
    analysis_count = fields.Integer(compute='get_analysis_count',
                                    help="This is the number of analysis linked with this request.")
    product_ids = fields.One2many('lims.request.product.pack', 'request_id', 'Products')
    is_request_complete = fields.Boolean(compute='compute_is_request_complete',
                                         help="This is checked if there are samples on this request.")
    product_id = fields.Many2one('product.product', 'Product',  domain=[('lims_for_analysis', '=', True)])
    comment = fields.Html('External comment',
                          help='Additional comment addressed to the customer (will be printed on analysis report)')
    note = fields.Text('Internal note',
                       help="Additional comment addressed to the internal team (won't be printed on analysis report)")
    date_plan = fields.Datetime('Date Plan', index=True, default=fields.Datetime.now, copy=False,
                                help="If this date is modified, it will be copied on these analysis that have no ones.")
    incomplete = fields.Boolean(compute='compute_incomplete', help="This is checked if one his analysis is incomplete.")
    nb_sop = fields.Integer('Tests', compute='compute_nb_sop', store=True, compute_sudo=True,
                            help="This is the number of tests of analysis linked to that request.")
    cancel_reason = fields.Char(tracking=True, copy=False)
    analysis_state = fields.Selection('get_analysis_state_selection', compute='compute_analysis_state', index=True, copy=False,
                                      help="If all his associated analysis, without those who are in 'Cancelled' stage, "
                                           "are in 'Second validation' stage, then if one among them is "
                                           "not conform/conform/unconclusive (in this priority order of verification), "
                                           "then the state of the request will be fail/conform/unconclusive. "
                                           "Nevertheless, if the laboratory have the checkbox 'Unconclusvive priority' "
                                           "that is checked, the priority order of verification will be change so that "
                                           "if one of them is not conform/unconclusive/conform, then the state "
                                           "of the request will be fail/unconclusive/conform respectively.")
    display_calendar = fields.Char(compute='get_display_name_calendar')
    date_report = fields.Datetime('Date Report', index=True, copy=False)
    salesperson = fields.Many2one('res.users', 'Salesperson')
    date_sample_begin = fields.Datetime('Analysis start date', index=True, compute='compute_date_sample_begin',
                                        store=True, copy=False,
                                        help="This date will be the earliest 'Start Date' of these analysis.")
    warning_update_analysis = fields.Boolean()
    is_receipt_send = fields.Boolean()
    kanban_state = fields.Selection([
        ('normal', 'Draft'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State', copy=False, default='normal', tracking=True,
        help="This is the availability state of the request. When the request switch to a new state, "
             "the kanban state comes back to 'Draft'.")

    @api.onchange('labo_id')
    def onchange_laboratory_id(self):
        if self.labo_id and not self.env.context.get('default_request_type_id'):
            self.request_type_id = self.labo_id.default_request_category_id

    @api.depends('name', 'partner_id')
    def get_display_name_calendar(self):
        """
        Compute the display_name used in calendar
        :return:
        """
        for record in self:
            record.display_calendar = " - ".join({record.name, record.partner_id.name or ''})

    def get_analysis_state_selection(self):
        """
        Return different state possible for the request
        :return: table of tuple
        """
        return [
            ('fail', _('Fail')),
            ('pass', _('Pass')),
            ('unconclusive', _('Inconclusive')),
        ]

    def compute_analysis_state(self):
        """
        Compute the analysis state
        :return:
        """
        cancel_stage_id = self.env['lims.analysis.stage'].search([('type', '=', 'cancel')], limit=1)
        validated2_stage_id = self.env['lims.analysis.stage'].search([('type', '=', 'validated2')], limit=1)
        for record in self:
            if record.analysis_ids.mapped('stage_id') == validated2_stage_id \
                    or record.analysis_ids.mapped('stage_id') == (cancel_stage_id + validated2_stage_id):
                analysis_validated_2_ids = record.analysis_ids.filtered(lambda a: a.stage_id == validated2_stage_id)
                if record.labo_id.unconclusive_priority:
                    record.analysis_state = analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'not_conform') and 'fail' \
                                            or analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'unconclusive') and 'unconclusive' \
                                            or analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'conform') and 'pass' \
                                            or False
                else:
                    record.analysis_state = analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'not_conform') and 'fail' \
                                            or analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'conform') and 'pass' \
                                            or analysis_validated_2_ids.filtered(
                        lambda a: a.state == 'unconclusive') and 'unconclusive' \
                                            or False
            else:
                record.analysis_state = False

    def duplicate_with_line(self):
        """
        Copy the request (with product_ids), display the duplicate request if only one is duplicated
        :return:
        """
        new_request_ids = self.env['lims.analysis.request']
        for record in self:
            duplicate_request = record.copy()
            for product in record.product_ids:
                duplicate_product = product.copy()
                duplicate_request.product_ids += duplicate_product
            new_request_ids += duplicate_request
            if self.env.context.get('copy_product_group'):
                for product_group_id in record.product_group_ids:
                    duplicate_product_group_i = product_group_id.copy()
                    duplicate_request.product_group_ids += duplicate_product_group_i
        return {'name': (_('Analysis Request')),
                'view_mode': 'tree,form,pivot,graph,calendar,activity',
                'res_model': 'lims.analysis.request',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', new_request_ids.ids)],
                }

    def compute_incomplete(self):
        """
        If one analysis is incomplete then the request is incomplete
        :return:
        """
        for record in self:
            record.incomplete = True if record.filtered(lambda r: r.analysis_ids.filtered(lambda a: a.is_incomplete)) \
                else False

    @api.depends('analysis_ids', 'analysis_ids.sop_ids')
    def compute_nb_sop(self):
        """
        Compute the number of SOPs
        :return:
        """
        for record in self:
            if record.analysis_ids:
                record.nb_sop = self.env['lims.sop'].search_count([('analysis_id', 'in', record.analysis_ids.ids)])
            else:
                record.nb_sop = 0

    def open_sop(self):
        """
        Open the view on SOPs of this request
        :return:
        """
        self.ensure_one()
        sop_ids = self.analysis_ids.mapped('sop_ids')
        form = self.env.ref('lims_base.lims_sop_form', False)
        tree = self.env.ref('lims_base.lims_sop_tree', False)
        return {
            'name': 'Test ',
            'type': 'ir.actions.act_window',
            'res_model': 'lims.sop',
            'view_id': tree.id,
            'view_mode': 'tree,form',
            'target': 'current',
            'views': [(tree.id, 'tree'),
                      (form.id, 'form')],
            'domain': [('id', 'in', sop_ids.ids)],
        }

    def write(self, vals):
        """
        if date_plan is in the vals then set date plan in analysis (without date_plan) with the same value
        :param vals:
        :return:
        """
        if ('state' in vals) and ('kanban_state' not in vals):
            vals['kanban_state'] = 'normal'
        res = super(LimsAnalysisRequest, self).write(vals)
        if vals.get('date_plan'):
            analysis_ids = self.analysis_ids.filtered(lambda a: not a.date_plan)
            if analysis_ids:
                analysis_ids.write({'date_plan': vals.get('date_plan')})
        return res

    def get_request_state(self):
        """
        Get the different state possible for the request
        :return: table of tuple
        """
        return [
            ('draft', _('Draft')),
            ('accepted', _('Accepted')),
            ('in_progress', _('In Progress')),
            ('done', _('Done')),
            ('report', _('Report')),
            ('cancel', _('Cancelled')),
        ]

    def compute_is_request_complete(self):
        """
        Compute is the request is complete
        :return:
        """
        for record in self:
            record.is_request_complete = record.is_request_ok()

    def is_request_ok(self):
        """
        Check if all sample_ids necessary are there
        :return:
        """
        self.ensure_one()
        return self.sample_ids

    @api.onchange('sample_ids')
    def onchange_sample_ids(self):
        """
        Compute is the request is complete
        :return:
        """
        self.compute_is_request_complete()

    @api.depends('analysis_ids')
    def get_analysis_count(self):
        """
        Get the number of analysis
        :return:
        """
        for record in self:
            record.analysis_count = len(record.analysis_ids)

    def open_analysis(self):
        """
        Open the analysis view
        :return:
        """
        self.ensure_one()
        return {
            'name': _('Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'lims.analysis',
            'view_mode': 'tree,form,pivot,graph,calendar',
            'target': 'current',
            'domain': [('request_id', '=', self.id)],
        }

    def do_confirmed(self):
        """
        Pass the request in state "accepted", set the order date in the request with value "today"
        :return:
        """
        self.write({
            'state': 'accepted',
            'order_date': fields.Date.today()
        })

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create the request and set the name of the request with the sequence of the laboratory
        :param vals_list:
        :return:
        """
        for vals in vals_list:
            labo = self.env['lims.laboratory'].search([('id', '=', vals.get('labo_id'))])
            if labo.seq_request_id:
                vals.update({'name': labo.seq_request_id.next_by_id()})
            else:
                raise exceptions.UserError(_('No sequence for the request in the laboratory'))
        res = super(LimsAnalysisRequest, self).create(vals_list)
        return res

    def get_values_for_create_sample(self, product_id, packs, regulation):
        vals = {
            'sequence': product_id.sequence,
            'name': product_id.name,
            'product_id': product_id.product_id.id,
            'request_id': self.id,
            'regulation_id': regulation.id if regulation else False,
            'matrix_id': product_id.matrix_id.id,
            'product_pack_id': product_id.id,
            'auto': True,
            'pack_ids': [(4, pack_id.id) for pack_id in packs[regulation]] if packs.get(regulation) else False,
            'date_plan': self.date_plan,
            'comment': product_id.comment,
            'method_param_charac_ids': [(4, method_param_charac_ids.id) for
                                        method_param_charac_ids in product_id.method_param_charac_ids.filtered(
                    lambda m: m.regulation_id == regulation)],
        }
        if product_id.pack_ids.filtered(lambda p: p.is_pack_of_pack):
            vals['pack_of_pack_ids'] = [(4, pack_id.id) for pack_id in product_id.pack_ids.filtered(
                lambda p: p.is_pack_of_pack)]
        return vals

    def generate_request_sample_line(self):
        vals_list = []
        request_sample_obj = self.env['lims.analysis.request.sample']
        product_ids = self.product_ids.filtered(lambda p: p.pack_ids or p.method_param_charac_ids)
        if not product_ids:
            raise exceptions.UserError(_(
                "There is no request line with parameter or pack to generate the sample line."))
        for product_id in product_ids:
            packs = {}
            all_pack = self.env['lims.parameter.pack']
            all_pack += product_id.pack_ids.filtered(lambda p: not p.is_pack_of_pack)
            all_pack += product_id.pack_ids.filtered(lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id')
            for pack_id in all_pack:
                if pack_id.regulation_id not in packs:
                    packs.update({
                        pack_id.regulation_id: [pack_id]
                    })
                else:
                    packs[pack_id.regulation_id].append(pack_id)
            regulation_ids = all_pack.mapped('regulation_id') + \
                             product_id.method_param_charac_ids.mapped('regulation_id')
            for regulation_id in set(regulation_ids):
                i = product_id.qty - \
                    len(product_id.request_sample_ids.filtered(lambda r: r.regulation_id.id == regulation_id.id))
                if not i and product_id.request_sample_ids:
                    request_sample_ids = product_id.request_sample_ids.filtered(
                        lambda r: r.regulation_id.id == regulation_id.id)
                    for request_sample_id in request_sample_ids:
                        request_sample_id.write(self._prepare_update_request_sample_line(request_sample_id, product_id))
                vals_list = self._prepare_new_request_sample_line(i, product_id, packs, regulation_id, vals_list)
        request_sample_obj.create(vals_list)

    def _prepare_update_request_sample_line(self, request_sample_id, product_id, update_elements=None):
        update_elements = update_elements or {}
        if len(request_sample_id.pack_ids) != len(
                product_id.pack_ids.filtered(lambda p: not p.is_pack_of_pack)):
            pack_ids = product_id.pack_ids.filtered(
                lambda p: not p.is_pack_of_pack and p.regulation_id == request_sample_id.regulation_id)
            pack_ids += product_id.pack_ids.filtered(
                lambda p: p.is_pack_of_pack).mapped('pack_of_pack_ids.pack_id').filtered(
                lambda p: p.regulation_id == request_sample_id.regulation_id)
            update_elements['pack_ids'] = pack_ids
        if len(request_sample_id.method_param_charac_ids) != len(product_id.method_param_charac_ids):
            update_elements['method_param_charac_ids'] = product_id.method_param_charac_ids.filtered(
                lambda m: m.regulation_id == request_sample_id.regulation_id)
        return update_elements

    def _prepare_new_request_sample_line(self, i, product_id, packs, regulation_id, vals_list=None):
        vals_list = vals_list or []
        while i > 0:
            vals = self.get_values_for_create_sample(product_id, packs, regulation_id)
            vals_list.append(vals)
            i -= 1
        return vals_list

    def create_analysis_wizard(self):
        """
        Open the wizard for create the analysis
        :return:
        """
        self.ensure_one()
        report_action = self.env['ir.actions.act_window']._for_xml_id('lims_base.create_analysis_wizard_action')
        report_action['context'] = {'default_analysis_request': self.id}
        return report_action

    def create_analysis(self, reception_date, sample_and_due_date, sample_ids=None):
        """
        Create all the analysis, set the date sample receipt in the analysis, set the due date in the analysis
        Create the result for each analysis, Pass the analysis in stage "plan"
        :param reception_date:  the reception date of the sample
        :param sample_and_due_date: the due_date
        :return:
        """
        plan_stage_id = self.env['lims.result.stage'].search([('type', '=', 'plan')], limit=1)
        if not plan_stage_id:
            raise exceptions.UserError('Plan stage not found ! Check the result stage')
        ana_obj = self.env['lims.analysis']
        sample_ids = sample_ids or self.sample_ids
        analysis_ids = self.sample_ids.mapped('analysis_id')
        # Take all result from analysis (usefull to not re-create the result a second time)
        method_param_from_res = analysis_ids.method_param_charac_ids
        method_param_from_res += analysis_ids.pack_ids.parameter_ids.method_param_charac_id - method_param_from_res
        method_param_from_res -= analysis_ids.get_parameters()
        # Fill the array with result
        tab_result = self.fill_tab_result(sample_ids, method_param_from_res)
        result_nu_obj = self.env['lims.analysis.numeric.result']
        result_sel_obj = self.env['lims.analysis.sel.result']
        result_ca_obj = self.env['lims.analysis.compute.result']
        result_tx_obj = self.env['lims.analysis.text.result']
        vals_num = []
        vals_se = []
        vals_ca = []
        vals_tx = []
        # Fill the 4 vals_list to prepare the creation
        for sample_id in sample_ids:
            if not sample_id.analysis_id:
                analysis_vals = self.add_analysis_values(sample_id, sample_info=sample_and_due_date.get(sample_id.id))
                ana_id = ana_obj.create(analysis_vals)
                analysis_ids += ana_id
                sample_id.update({'analysis_id': ana_id.id})
            vals = sample_and_due_date.get(sample_id.id) or {}
            if reception_date:
                vals.update({'date_sample_receipt': reception_date})
            if vals:
                sample_id.analysis_id.write(vals)
            analysis_id = sample_id.analysis_id
            analysis_parameters = analysis_id.get_parameters()
            all_pack = sample_id.pack_of_pack_ids.pack_of_pack_ids.pack_id
            all_pack += sample_id.pack_ids - all_pack
            for pack_id in all_pack:
                for method_param_id in pack_id.parameter_ids.method_param_charac_id - analysis_parameters:
                    self.create_result(analysis_id, method_param_id, tab_result, plan_stage_id, vals_num, vals_se,
                                       vals_ca, vals_tx)
                    for conditional in method_param_id.conditional_parameters_ids:
                        self.create_result(analysis_id, conditional, tab_result, plan_stage_id, vals_num, vals_se,
                                           vals_ca, vals_tx)
            for method_param_id in sample_id.method_param_charac_ids - analysis_parameters:
                self.create_result(analysis_id, method_param_id, tab_result, plan_stage_id, vals_num, vals_se, vals_ca,
                                   vals_tx)
                for conditional in method_param_id.conditional_parameters_ids:
                    self.create_result(analysis_id, conditional, tab_result, plan_stage_id, vals_num, vals_se,
                                       vals_ca, vals_tx)
            update_vals = {}
            new_methods = sample_id.method_param_charac_ids - sample_id.analysis_id.method_param_charac_ids
            new_packs = sample_id.pack_ids - sample_id.analysis_id.pack_ids
            if new_methods:
                update_vals['method_param_charac_ids': [(4, x.id) for x in new_methods]]
            if new_packs:
                update_vals['pack_ids': [(4, x.id) for x in new_packs]]
            sample_id.analysis_id.write(update_vals)
        # Create result
        for val in vals_num:
            result = result_nu_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            limits_num = tab_result[val.get('method_param_charac_id')].limit_result_ids
            result_vals = result.get_result_vals(specific_vals={'limit_results': limits_num})
            result.update(result_vals)
        for val in vals_se:
            result = result_sel_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            result.update(result.get_result_vals())
        for val in vals_ca:
            result = result_ca_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            limits_compute = tab_result[val.get('method_param_charac_id')].limit_compute_result_ids
            result_vals = result.get_result_vals(specific_vals={'limit_results': limits_compute})
            result.update(result_vals)
        for val in vals_tx:
            result = result_tx_obj.with_context(lang=None, no_limit=True, bypass=True).create(val)
            result.update(result.get_result_vals())
        sample_ids.analysis_id.create_sop()
        plan_stage_id = self.env['lims.analysis.stage'].sudo().search([('type', '=', 'plan')], limit=1)
        analysis_ids.filtered(lambda a: a.rel_type in [False, 'draft']).do_plan(plan_stage_id)
        self.invalidate_recordset()

    def fill_tab_result(self, sample_ids, method_param=False):
        """
        Fill a tab with all necessary result (from all sample of this request)
        :param analysis_request:
        :return:
        """
        tab_result = {}
        all_pack = self.env['lims.parameter.pack']
        all_pack += sample_ids.pack_of_pack_ids.pack_of_pack_ids.pack_id
        all_pack += sample_ids.pack_ids - all_pack
        method_param_charac_ids = sample_ids.method_param_charac_ids

        if method_param:
            method_param_charac_ids += method_param
        for method_param_charac_id in method_param_charac_ids:
            tab_result = self._insert_in_tab_result(tab_result, method_param_charac_id)
            for conditional_parameters_id in method_param_charac_id.conditional_parameters_ids:
                tab_result = self._insert_in_tab_result(tab_result, conditional_parameters_id)
        for pack_line_id in all_pack.parameter_ids:
            pack_id = pack_line_id.pack_id
            method_param_ids = pack_line_id.method_param_charac_id
            for method_param_id in method_param_ids:
                tab_result = self._insert_in_tab_result(tab_result, method_param_id, pack_id)
                for conditional_parameters_id in method_param_id.conditional_parameters_ids:
                    tab_result = self._insert_in_tab_result(tab_result, conditional_parameters_id)
        return tab_result

    def _insert_in_tab_result(self, tab_result, method_param_charac_id, pack_id=False):
        if not tab_result.get(method_param_charac_id.id):
            result_nu_obj = self.env['lims.analysis.numeric.result']
            result_sel_obj = self.env['lims.analysis.sel.result']
            result_ca_obj = self.env['lims.analysis.compute.result']
            result_tx_obj = self.env['lims.analysis.text.result']
            result_vals = {
                'method_param_charac_id': method_param_charac_id.id,
            }
            if pack_id:
                result_vals['pack_id'] = pack_id.id
            if method_param_charac_id.format == 'nu':
                tab_result[method_param_charac_id.id] = result_nu_obj.create(result_vals)
            elif method_param_charac_id.format == 'se':
                tab_result[method_param_charac_id.id] = result_sel_obj.create(result_vals)
            elif method_param_charac_id.format == 'ca':
                tab_result[method_param_charac_id.id] = result_ca_obj.create(result_vals)
            elif method_param_charac_id.format == 'tx':
                tab_result[method_param_charac_id.id] = result_tx_obj.create(result_vals)
        return tab_result

    def create_result(self, analysis_id, method_param_id, tab_result, plan_stage_id, vals_num, vals_se, vals_ca,
                      vals_tx):
        """
        create (copy) result from the tab_result with necessary information
        :param analysis_id:
        :param method_param_id:
        :param tab_result:
        :param default:
        :param plan_stage_id:
        :return:
        """
        default = {'analysis_id': analysis_id.id}
        sop_id = analysis_id.mapped('sop_ids').filtered(
            lambda s: s.method_id == method_param_id.method_id and s.rel_type != 'cancel')
        if sop_id:
            default.update({'sop_id': sop_id.id})
        if not sop_id or sop_id.rel_type == 'draft':
            default.update({'stage_id': plan_stage_id.id})
        format = method_param_id.format
        vals = tab_result[method_param_id.id].copy_data(default=default)[0]
        if format == 'nu':
            if not any(vals.get('method_param_charac_id') == val_num.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_num.get('analysis_id') for val_num in vals_num):
                vals_num.append(vals)
        elif format == 'se':
            if not any(vals.get('method_param_charac_id') == val_se.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_se.get('analysis_id') for val_se in vals_se):
                vals_se.append(vals)
        elif format == 'ca':
            if not any(vals.get('method_param_charac_id') == val_ca.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_ca.get('analysis_id') for val_ca in vals_ca):
                vals_ca.append(vals)
        elif format == 'tx':
            if not any(vals.get('method_param_charac_id') == val_tx.get('method_param_charac_id') and
                       vals.get('analysis_id') == val_tx.get('analysis_id') for val_tx in vals_tx):
                vals_tx.append(vals)

    def add_analysis_values(self, sample_id, sample_info=False):
        """
        Get the value for create one analysis
        :param sample_id: one sample from sample_ids of the request
        :param sample_info: information sent by the analysis creation wizard
        :return:
        """
        if not sample_info:
            sample_info = {}
        analysis_vals = {
            'request_id': self.id,
            'regulation_id': sample_id.regulation_id.id,
            'matrix_id': sample_id.matrix_id.id,
            'laboratory_id': self.labo_id.id,
            'sample_name': sample_id.name,
            'partner_id': self.partner_id.id,
            'note': sample_id.comment,
            'date_plan': sample_info.get('date_plan') or sample_id.date_plan,
            'date_sample': sample_info.get('date_sample'),
            'customer_ref': self.customer_ref,
            'sample_id': sample_id.id,
            'due_date': sample_info.get('due_date'),
            'category_id': sample_info.get('category_id'),
            'pack_ids': [(4, pack_id.id) for pack_id in sample_id.pack_ids],
            'pack_of_pack_ids': [(6, 0, sample_id.pack_of_pack_ids.ids)],
            'method_param_charac_ids': [(4, method_param.id) for method_param in sample_id.method_param_charac_ids],
            'partner_contact_ids': [(4, contact) for contact in sample_info.get('partner_contact_ids', [])],
            'dilution_factor': sample_id.dilution_factor
        }
        if sample_id.product_pack_id and sample_id.product_pack_id.product_id:
            analysis_vals.update({
                'product_id': sample_id.product_pack_id.product_id.id,
            })
        return analysis_vals

    def do_cancel(self):
        """
        Pass the request in state "cancel", pass the analysis in stage "cancel" if the analysis is plan/draft
        :return:
        """
        analysis_obj = self.env['lims.analysis']
        analysis_obj.search([('request_id', 'in', self.ids), ('rel_type', 'in', ['plan', 'draft'])]).do_cancel()
        self.write({
            'state': 'cancel',
        })

    def check_done_state(self):
        """
        Request is done when all analysis are in states validation2 or cancel
        :return:
        """
        for record in self:
            if all(a.stage_id.type == 'cancel' for a in record.analysis_ids):
                record.do_cancel()
            elif not record.analysis_ids. \
                    filtered(lambda a: a.stage_id.type in ['plan', 'draft', 'todo', 'wip', 'done', 'validated1']):
                record.state = 'done'

    @api.onchange('partner_id')
    def get_default_salesperson(self):
        """
        Search for the sale person by default in the customer contact, and his first parent element
        :return:
        """
        if not self.salesperson:
            if self.partner_id.user_id:
                self.salesperson = self.partner_id.user_id
            if not self.partner_id.user_id and self.partner_id.parent_id.user_id:
                self.salesperson = self.partner_id.parent_id.user_id

    @api.depends('analysis_ids', 'analysis_ids.date_start')
    def compute_date_sample_begin(self):
        for record in self:
            if not record.analysis_ids:
                record.date_sample_begin = False
            else:
                lastest_analysis_ids = record.analysis_ids.filtered('date_start').sorted(key=lambda a: a.date_start)
                record.date_sample_begin = lastest_analysis_ids[0].date_start if lastest_analysis_ids else False

    def action_send_receipt(self, module='lims_base', template='email_template_request_receipt'):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup("%s.%s" % (module, template))[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup("%s.%s" % ('mail', 'email_compose_message_wizard_form'))[2]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'lims.analysis.request',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'mark_receipt_as_sent': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_receipt_as_sent'):
            self.with_context(tracking_disable=True).write({'is_receipt_send': True})
        return super(LimsAnalysisRequest, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def do_cancel_request_wizard(self):
        self.ensure_one()
        return {
            'name': _('Cancel request analysis'),
            'type': 'ir.actions.act_window',
            'view_form': 'form',
            'view_mode': 'form',
            'res_model': 'request.cancel.wizard',
            'context': {'default_request_id': self.id},
            'target': 'new',
        }

    def archive_cascade(self):
        """
        Toggle active for request, analysis, sop and result
        :return:
        """
        analysis_ids = self.env['lims.analysis'].with_context(active_test=False).search(
            [('request_id', 'in', self.ids)])
        sop_ids = self.env['lims.sop'].with_context(active_test=False).search([('analysis_id', 'in', analysis_ids.ids)])
        sop_ids.toggle_active()
        for record in self:
            record.toggle_active()
            for analysis_id in analysis_ids.filtered(lambda x: x.request_id.id == record.id):
                analysis_id.result_num_ids.toggle_active()
                analysis_id.result_compute_ids.toggle_active()
                analysis_id.result_sel_ids.toggle_active()
                analysis_id.result_text_ids.toggle_active()
                analysis_id.toggle_active()

            # Nb sop doesn't update after archive / Unarchive
            record.nb_sop = self.env['lims.sop'].search_count([('rel_request_id', '=', record.id)])

    def _message_get_suggested_recipients(self):
        """
        Add partner and partner contact to the message sending box as suggestion
        (checkbox to send message so those partners and add them as followers)
        """
        recipients = super(LimsAnalysisRequest, self)._message_get_suggested_recipients()
        try:
            for record in self:
                if record.partner_id:
                    record._message_add_suggested_recipient(recipients, partner=record.partner_id, reason=_('Customer'))
                for partner_id in record.partner_contact_ids:
                    record._message_add_suggested_recipient(recipients, partner=partner_id, reason=_('Contact'))
        except exceptions.AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        res = super(LimsAnalysisRequest, self)._message_auto_subscribe_followers(updated_values, default_subtype_ids)
        if self.env['ir.config_parameter'].sudo().get_param('is_automatic_customer_follower'):
            if updated_values.get('partner_id'):
                res.append((updated_values.get('partner_id'), default_subtype_ids, False))
            if updated_values.get('partner_contact_ids'):
                contact_vals = updated_values.get('partner_contact_ids')
                # many2many vals can be presented on format ([6, 0, ids], (Command.set: 6, 0, [ids]) or (4, id)].
                # We must handle all cases
                if isinstance(contact_vals[0], list):
                    contact_ids = contact_vals[0][2]
                elif isinstance(contact_vals[0], tuple):
                    if len(contact_vals[0]) == 3:
                        contact_ids = contact_vals[0][2]
                    else:
                        contact_ids = [contact[1] for contact in contact_vals]
                else:
                    return res
                for contact_id in contact_ids:
                    res.append((contact_id, default_subtype_ids, False))
        return res

    def _compute_access_url(self):
        super()._compute_access_url()
        for request in self:
            request.access_url = f'/my/requests/{request.id}'

    def get_comment(self):
        self.ensure_one()
        return self.comment if bool(html2plaintext(self.comment)) else False

    def get_request_packs_and_pack_of_packs(self):
        packs = self.env['lims.parameter.pack']
        for record in self.filtered(lambda r: r.state != 'cancel'):
            packs += record.sample_ids.get_sample_packs_and_pack_of_packs()
        return packs

    def clean_results(self, limit=500):
        """
        When creating results from a request, 'dummy' results are created and duplicated for performance issues. But
        those results are never linked to an analysis, nor deleted. This function is called by cron clean_result_cron
        to do the job (deleting results after creation from request will slow down the process).
        :param limit: number of results to delete before committing (used to save some changes if a timeout must occur)
        :return: None
        """
        result_ids = self.env['lims.analysis.numeric.result'].search([('analysis_id', '=', False)])
        result_sel_ids = self.env['lims.analysis.sel.result'].search([('analysis_id', '=', False)])
        result_compute_ids = self.env['lims.analysis.compute.result'].search([('analysis_id', '=', False)])
        result_text_ids = self.env['lims.analysis.text.result'].search([('analysis_id', '=', False)])
        results = list(result_ids) + list(result_sel_ids) + list(result_compute_ids) + list(result_text_ids)
        i = 0
        for result in results:
            result.with_context(bypass_checks=True).unlink()
            i += 1
            if i == limit:
                self.env.cr.commit()
                i = 0

    def get_analyses_filtered(self, remove_stage: list = None, domain=None):
        """
        Get analyses from analyses, can get filtered analysis_ids.
        Usually all stage will be taken except "cancel"
        So it become : analysis.get_analyses_filtered(remove_stage=['cancel'])
        Or can directly set a specific Lambda to use : analysis.get_analyses_filtered(domain=lambda s: s.priority == 1)
        :param remove_stage:
        :param domain:
        :return:
        """
        if remove_stage:
            domain = lambda r: r.rel_type not in remove_stage
        return self.analysis_ids.filtered(domain) if domain else self.analysis_ids
