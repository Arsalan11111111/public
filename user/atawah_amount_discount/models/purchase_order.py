# -*- coding: utf-8 -*-
""" Purchase Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError
from datetime import timedelta,date,datetime
import datetime


class PurchaseOrder(models.Model):
    """ inherit Purchase Order """
    _inherit = 'purchase.order'

    check_lock_pass = fields.Boolean(default=True)



    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for po in self:
            lock_date = po.company_id._get_user_fiscal_lock_date()
            if lock_date:
                if po.date_order.date() <= lock_date:
                    po.check_lock_pass = True
        return res

    def button_cancel(self):
        for po in self:
            lock_date = po.company_id._get_user_fiscal_lock_date()

            if po.date_order.date() <= lock_date:
                if po.check_lock_pass == True:
                    raise UserError(_('You cannot add/modify Purchase Order prior to and inclusive of the lock date'))
                else:
                    res = super(PurchaseOrder, self).button_cancel()
            else:
                res = super(PurchaseOrder, self).button_cancel()

        return True


    def button_draft(self):
        for po in self:
            lock_date = po.company_id._get_user_fiscal_lock_date()
            if po.date_order.date() <= lock_date:
                if po.check_lock_pass == True:
                    raise UserError(_('You cannot add/modify Purchase Order prior to and inclusive of the lock date'))
                else:
                    res = super(PurchaseOrder, self).button_draft()
            else:
                res = super(PurchaseOrder, self).button_draft()
        return True

    def action_check_lock_pass(self):
        """ :return Project Message action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'check.lock.pass',
            'name': _('Inter Pass'),
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
        }

    @api.constrains('partner_ref')
    def _check_unique_bill_reference(self):
        for record in self:
            if record.partner_ref:
                duplicates = self.env['purchase.order'].search(
                    [('partner_ref', '=', record.partner_ref), ('id', '!=', record.id)])
                if duplicates:
                    raise ValidationError('The bill reference must be unique!')






    def fully_billed(self):
        # for record in self:
            # record.invoice_status = 'invoiced'
        self.invoice_status = 'invoiced' 