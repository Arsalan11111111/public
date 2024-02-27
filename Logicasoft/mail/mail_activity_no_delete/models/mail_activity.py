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

from odoo import models, fields, api, exceptions, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    active = fields.Boolean(default=True)

    def unlink(self):
        for activity in self:
            if activity.date_deadline <= fields.Date.today():
                self.env['bus.bus']._sendmany(
                    [[activity.user_id.partner_id, 'mail.activity/updated', {'activity_deleted': True}]]
                )

            activity.write({
                'active': False,
            })
        return True

    def activity_format(self):
        activities = [act for act in self.read() if act.get('active')]
        mail_template_ids = {template_id for activity in activities for template_id in activity["mail_template_ids"]}
        mail_template_info = self.env["mail.template"].browse(mail_template_ids).read(['id', 'name'])
        mail_template_dict = {mail_template['id']: mail_template for mail_template in mail_template_info}
        for activity in activities:
            activity['mail_template_ids'] = [
                mail_template_dict[mail_template_id] for mail_template_id in activity['mail_template_ids']
            ]
        return activities

