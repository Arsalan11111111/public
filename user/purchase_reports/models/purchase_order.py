""" Purchase Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError

from num2words import num2words


class PurchaseOrder(models.Model):
    """
        Inherit Purchase Order:
         -
    """
    _inherit = 'purchase.order'

    qa_text = fields.Char(
        default='QA-FRM-28,Issue:01,Rev:07,Rev.Date:08..2.2021', string="Label")
    notes = fields.Html(
        string='Terms and Conditions',
        default=lambda self: self.env.company.purchase_terms_condition
    )

    contact_person = fields.Text(compute='_compute_contact_person', store=True)

    @api.depends('partner_id')
    def _compute_contact_person(self):
        """ Compute contact_person value """
        for rec in self:
            rec.contact_person = ""
            if rec.partner_id:
                if rec.partner_id.mobile:
                    rec.contact_person = "(" + rec.partner_id.mobile + ")"
                if rec.contact_person and rec.partner_id.email:
                    rec.contact_person = rec.contact_person + \
                        "(" + rec.partner_id.email + ")"
                # if rec.partner_id.notes:
                #     rec.notes=rec.partner_id.notes

    def get_amount_in_word(self, amount):
        """ Get Amount In Word """
        lang = self.env.user.lang
        currency = self.currency_id
        text = ''
        if lang == 'en_US':
            text += num2words(int((str(amount).split('.')[0])),
                              lang='en') + ' ' + currency.currency_unit_label + '  '
            text += num2words(int((str(amount).split('.')[1])),
                              lang='en') + ' ' + currency.currency_subunit_label
        return text.title()
