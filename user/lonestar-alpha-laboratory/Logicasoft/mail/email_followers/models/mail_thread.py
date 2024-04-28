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

from odoo import api, models, tools, _
from html import unescape


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype_xmlid=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        """
        If the message is a comment or an email and has followers, add at the end of the mail
        a list of all the followers.
        :param body: Body of the message
        :param subject: Subject of the message
        :param message_type: Type of the message
        :param subtype: Subtype of the message
        :param parent_id: Parent of the message
        :param attachments: Attachments
        :param content_subtype: Subtype of the content
        :param kwargs:
        :return:
        """

        def _guess_lang(self):
            if 'lang' in self.env.context:
                lang = self.env.context['lang']
            elif 'partner_id' in self._fields:
                lang = self.partner_id.lang
            elif self.env.lang:
                lang = self.env.lang
            else:
                lang = self.env.user.lang
            return lang

        # magic variable used by Odoo:
        context = {'lang': _guess_lang(self)}
        original_body = body

        follower_display_type = self.env['ir.config_parameter'].sudo().get_param('mail.followers.display_type')
        if not follower_display_type:
            self.env['ir.config_parameter'].sudo().set_param('mail.followers.display_type', 'simple')

        followers = ""
        partner_ids = self.env['res.partner']
        has_partners = (
            (self.message_follower_ids and len(self.message_follower_ids.filtered('partner_id')))
            or kwargs.get('partner_ids')
        )

        if has_partners and subtype_xmlid != 'mail.mt_note':
            partner_ids += self.message_follower_ids.mapped('partner_id')
            if kwargs.get('partner_ids'):
                partner_ids += self.env['res.partner'].search([('id', 'in', kwargs.get('partner_ids')),
                                                               ('id', 'not in', partner_ids.ids)])

            if follower_display_type == "bullet":
                follower_list = "<ul>"
                follower_list += ''.join(["<li>{}</li>".format(partner_id.display_name) for partner_id in partner_ids])
                follower_list += "</ul>"
            else:
                follower_list = ' - '.join([partner_id.display_name for partner_id in partner_ids])

            followers = ''.join([
                "<hr />",
                _("<p>This email is followed by:</p>"),
                follower_list,
                "",
            ])

            if partner_ids:
                body = tools.append_content_to_html(body, followers, plaintext=False)

        msg = super(MailThread, self).message_post(
            body=body,
            subject=subject,
            message_type=message_type,
            parent_id=parent_id,
            subtype_xmlid=subtype_xmlid,
            attachments=attachments,
            content_subtype=content_subtype,
            **kwargs,
        )

        if msg and not msg.notified_partner_ids:
            msg.write({
                'body': original_body,
            })

        return msg

