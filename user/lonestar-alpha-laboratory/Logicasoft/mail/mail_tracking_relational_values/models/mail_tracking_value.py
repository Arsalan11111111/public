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
from odoo import models, api


class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):
        # to avoid duplicate tracking lines:
        if hasattr(self.env[model_name], '_tracking_parent') and col_info.get('related'):
            return
        if col_info['type'] in ['one2many', 'many2many']:
            field = self.env['ir.model.fields']._get(model_name, col_name)
            if not field:
                return
            if col_info['type'] == 'one2many' and len(initial_value) > len(new_value):
                # If one line has been unlinked, we can't add the display_name of unlinked line because the unlinking is
                # already done, and we can't access the object
                old_value = ''
            else:
                old_value = ' • '.join(initial_value.mapped('display_name'))
            values = {
                'field': field.id,
                'field_desc': col_info['string'],
                'field_type': col_info['type'],
                'tracking_sequence': tracking_sequence,
                'old_value_char': old_value,
            }
            if new_value and type(new_value.mapped('display_name')) == str:
                values.update({'new_value_char': f" • {new_value.mapped('display_name')}"})
            return values
        return super(MailTrackingValue, self).create_tracking_values(
            initial_value, new_value, col_name, col_info, tracking_sequence, model_name)

    def _compute_field_groups(self):
        # overrided from standard addons (addons/mail/models/mail_tracking_value.py)
        for tracking in self:
            model = self.env[tracking.field.model]
            field = model._fields.get(tracking.field.name)
            tracking.field_groups = field.groups if field else 'base.group_system'

