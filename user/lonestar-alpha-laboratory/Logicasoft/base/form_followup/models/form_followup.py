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
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class FormFollowup(models.Model):
    _name = 'form.followup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Form Followup'

    @api.model
    def get_default_name(self):
        return _('New')

    name = fields.Char('Name', translate=1, required=1,
                       default=get_default_name)
    type_id = fields.Many2one('form.followup.type',
                              'Document type', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    product_tmpl_id = fields.Many2one('product.template', 'Product')
    reqdate = fields.Date('Requested date')
    recdate = fields.Date('Reception date')
    valdate = fields.Date('Validity date')
    last_sign_date = fields.Date('Last Signature Date')
    comment = fields.Html('Comment')
    rel_group_ids = fields.Many2many('res.groups', related='type_id.group_ids')
    rel_color = fields.Char(related='type_id.color')
    stage_id = fields.Many2one('form.followup.stage', 'Stage')
    tag_ids = fields.Many2many(
        'form.followup.tag', 'form_followup_tag_rel', 'form_followup_id', 'tag_id', string='Tags')
    active = fields.Boolean('Active', default=1)
    doc_name = fields.Char('Document Name')
    company_id = fields.Many2one('res.company', 'Company')
    start_date = fields.Datetime('Start Date')
    add_to_mail_composer = fields.Boolean('Attach to mail')
    document_folder_id = fields.Many2one('documents.folder', 'Document Folder')
    document_tag_ids = fields.Many2many(
        'documents.tag', string='Document Tags')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            form_type = self.env['form.followup.type'].browse(vals['type_id'])
            vals['name'] = form_type.sequence_id.next_by_code('form.followup')
        return super().create(vals_list)

    def open_line(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attachment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'current',
        }

    def check_late_reception(self):
        send_stage = self.env.user.company_id.send_mail_followup_stage_ids.ids
        if send_stage:
            followup_to_mail = self.env['form.followup'].search([
                ('stage_id', 'in', send_stage),
                ('reqdate', '!=', False),
                ('recdate', '=', False),
            ]).filtered(lambda f: f.type_id.mail_reception)
            url = self.env['ir.config_parameter'].search(
                [('key', '=', 'web.base.url')])
            for followup in followup_to_mail:
                template_id = followup.type_id.mail_reception
                old_body = template_id.body_html
                alert_date = followup.reqdate
                if followup.type_id and followup.type_id.delay_reception:
                    alert_date = alert_date + \
                        relativedelta(days=followup.type_id.delay_reception)
                if fields.Date.today() >= alert_date:
                    link = '%s/web#id=%s&view_type=form&model=%s' % (
                        url.value, followup.id, followup._name)
                    button_label = _('Show Form')
                    template_id.body_html = template_id.body_html + \
                        "</br><a href={}><button class='button btn btn-primary'>" \
                        "{}</button></a>".format(
                            link, button_label)
                    mail_vals = template_id.generate_email(followup.id)
                    mail_vals.update({
                        'recipient_ids': [(4, partner_id.id) for partner_id in
                                          followup.mapped('message_follower_ids.partner_id')],
                        'message_type': 'comment',
                        'notification': True,
                        'auto_delete': False})
                    mail_id = self.env['mail.mail'].create(mail_vals)
                    for partner_id in followup.mapped('message_follower_ids.partner_id'):
                        self.env['mail.notification'].create({
                            'mail_message_id': mail_id.mail_message_id.id,
                            'res_partner_id': partner_id.id,
                            'is_email': True,
                            'mail_id': mail_id.id,
                        })
                    mail_id.mail_message_id.needaction_partner_ids = followup.mapped(
                        'message_follower_ids.partner_id')
                    mail_id.send()
                    template_id.body_html = old_body

    def check_late_validity(self):
        send_stage = self.env.user.company_id.send_mail_followup_stage_ids.ids
        if send_stage:
            followup_to_mail = self.env['form.followup'].search([('stage_id', 'in', send_stage),
                                                                 ('valdate', '!=', False)]).\
                filtered(lambda f: f.type_id.mail_validity)
            url = self.env['ir.config_parameter'].search(
                [('key', '=', 'web.base.url')])
            for followup in followup_to_mail:
                template_id = followup.type_id.mail_validity
                old_body = template_id.body_html
                alert_date = followup.valdate
                if followup.type_id and followup.type_id.delay_validity:
                    alert_date = alert_date + \
                        relativedelta(days=followup.type_id.delay_validity)
                if fields.Date.today() >= alert_date:
                    link = '%s/web#id=%s&view_type=form&model=%s' % (
                        url.value, followup.id, followup._name)
                    button_label = _('Show Form')
                    template_id.body_html = template_id.body_html + \
                        "</br><a href={}><button class='button btn btn-primary'>" \
                        "{}</button></a>".format(
                            link, button_label)
                    mail_vals = template_id.generate_email(followup.id)
                    mail_vals.update({
                        'recipient_ids': [(4, partner_id.id) for partner_id in
                                          followup.mapped('message_follower_ids.partner_id')],
                        'message_type': 'comment',
                        'notification': True,
                        'auto_delete': False})
                    mail_id = self.env['mail.mail'].create(mail_vals)
                    for partner_id in followup.mapped('message_follower_ids.partner_id'):
                        self.env['mail.notification'].create({
                            'mail_message_id': mail_id.mail_message_id.id,
                            'res_partner_id': partner_id.id,
                            'is_email': True,
                            'mail_id': mail_id.id,
                        })
                    mail_id.mail_message_id.needaction_partner_ids = followup.mapped(
                        'message_follower_ids.partner_id')
                    mail_id.send()
                    template_id.body_html = old_body

    def write(self, vals):
        res = super().write(vals)
        if vals.get('document_folder_id') or vals.get('document_tag_ids'):
            attach_ids = self.env['ir.attachment'].search([('res_model', '=', 'form.followup'),
                                                           ('res_id', 'in', self.ids)])
            if vals.get('document_folder_id'):
                [attach_id.write(
                    {'folder_id': [(6, 0, attach_id.document_folder_id.ids)]}) for attach_id in attach_ids]
            if vals.get('document_tag_ids'):
                [attach_id.write(
                    {'tag_ids': [(6, 0, attach_id.document_tag_ids.ids)]}) for attach_id in attach_ids]
        return res

