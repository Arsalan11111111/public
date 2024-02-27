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


class LimsTourLine(models.Model):
    _name = 'lims.tour.line'
    _description = 'Lims Tour Line'
    _inherit = ['mail.thread']
    _tracking_parent = 'tour_id'
    _order = 'tour_id desc, sequence, id'
    _rec_name = 'analysis_id'
    _inherits = {'lims.analysis': 'analysis_id'}

    date = fields.Datetime(related='analysis_id.date_plan', store=True, string='Date plan')
    analysis_id = fields.Many2one('lims.analysis', 'Analysis', required=True, ondelete="cascade")
    on_site_result_num_ids = fields.One2many('lims.analysis.numeric.result', compute='get_on_site_result_ids',
                                             readonly=0)
    on_site_result_sel_ids = fields.One2many('lims.analysis.sel.result', compute='get_on_site_result_ids',
                                             readonly=0)
    on_site_result_compute_ids = fields.One2many('lims.analysis.compute.result', compute='get_on_site_result_ids',
                                                 readonly=0)
    on_site_result_text_ids = fields.One2many('lims.analysis.text.result', compute='get_on_site_result_ids',
                                              readonly=0)
    rel_partner_owner_id = fields.Many2one(related="sampling_point_id.partner_owner_id")
    sequence = fields.Integer('Sequence', default=1)
    time_float = fields.Float('Time', tracking=True)
    is_sampled = fields.Boolean(tracking=True)
    color_on_line = fields.Boolean(tracking=True)

    def write(self, vals):
        if vals.get('is_sampled'):
            vals['date_sample'] = not self.date_sample and (vals.get('date_sample') or fields.Datetime.now())
        return super().write(vals)

    def add_parameter(self):
        return {
            'name': _('Add parameters'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.parameters.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_id': self.analysis_id.id,
                        'default_tour_line_id': self.id}
        }

    def unlink(self):
        for record in self.filtered('tour_id'):
            record.tour_id.message_post(body=_('Tour line from {0} has been deleted by {1}').format(
                self.analysis_id.name, self.env.user.name))
            record.analysis_id.tour_id = False
        return super().unlink()

    def get_regulation(self):
        return self.analysis_id.regulation_id.ids or False

    def get_portal_url(self, portal_url=False):
        self.ensure_one()
        if not portal_url:
            return self.analysis_id.get_portal_url()
        action_id = self.tour_id.open_tour_analysis()
        return f"/web#id={self.id}&model={action_id.get('res_model')}&view_type=form&action={action_id.get('id')}"

    def get_on_site_result_ids(self):
        for record in self:
            record.on_site_result_num_ids = record.result_num_ids.filtered(lambda r: r.rel_is_on_site)
            record.on_site_result_sel_ids = record.result_sel_ids.filtered(lambda r: r.rel_is_on_site)
            record.on_site_result_compute_ids = record.result_compute_ids.filtered(lambda r: r.rel_is_on_site)
            record.on_site_result_text_ids = record.result_text_ids.filtered(lambda r: r.rel_is_on_site)


    def get_sent_reports(self, report_state=False, get_only_if_one=False):
        """
        this function is used to make the LIMS's report portal compatible
        :param report_state:
        :param get_only_if_one:
        :return:
        """
        report_ids = False
        try:
            report_ids = self.analysis_id.get_sent_reports(self, report_state=report_state,
                                                           get_only_if_one=get_only_if_one)
        finally:
            return report_ids
