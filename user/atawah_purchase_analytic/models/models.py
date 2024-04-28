# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class atawah_purchase_analytic(models.Model):
#     _name = 'atawah_purchase_analytic.atawah_purchase_analytic'
#     _description = 'atawah_purchase_analytic.atawah_purchase_analytic'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
