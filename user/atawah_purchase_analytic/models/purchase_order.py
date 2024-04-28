# -*- coding: utf-8 -*-
""" Purchase Order """
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class PurchaseOrder(models.Model):
    """ inherit Purchase Order """
    _inherit = 'purchase.order'

    analytic_distribution = fields.Json(string="Analytic Account")
    analytic_precision = fields.Integer(store=False,
                                        default=lambda self: self.env[
                                            'decimal.precision'].precision_get(
                                            "Percentage Analytic"), )
    analytic_name = fields.Text(compute='_compute_analytic_distribution_name',
                                store=True)

    total_in_omr = fields.Float(compute="_compute_omr_amount")

    @api.depends('analytic_distribution')
    def _compute_analytic_distribution_name(self):
        """ Compute analytic_distribution_name value """
        for rec in self:
            rec.analytic_name = ""
            if rec.analytic_distribution:
                for a in rec.analytic_distribution:
                    n = self.env['account.analytic.account'].search(
                        [('id', '=', a)], limit=1)
                    if not rec.analytic_name:
                        rec.analytic_name = "(" + n.name + ")"
                    else:
                        rec.analytic_name = rec.analytic_name + "(" + n.name + ")"


    @api.depends('currency_id','company_id','amount_total')
    def _compute_omr_amount(self):
        for rec in self:
            if rec.currency_id.id == rec.company_id.currency_id.id:
                    rec.total_in_omr = rec.amount_total
            else:
                search_rate = self.env['res.currency.rate'].search([('currency_id','=',rec.currency_id.id)], order='name desc', limit=1)
                if search_rate:
                    rec.total_in_omr = rec.amount_total / search_rate.company_rate
                else:
                    rec.total_in_omr = rec.amount_total


class AccountPayment(models.Model):
    """ inherit Account Payment """
    _inherit = 'account.payment'

    analytic_precision = fields.Integer(store=False,
                                        default=lambda self: self.env[
                                            'decimal.precision'].precision_get(
                                            "Percentage Analytic"))
