# -*- coding: utf-8 -*-
# from odoo import http


# class AtawahAmountDiscount(http.Controller):
#     @http.route('/atawah_amount_discount/atawah_amount_discount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/atawah_amount_discount/atawah_amount_discount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('atawah_amount_discount.listing', {
#             'root': '/atawah_amount_discount/atawah_amount_discount',
#             'objects': http.request.env['atawah_amount_discount.atawah_amount_discount'].search([]),
#         })

#     @http.route('/atawah_amount_discount/atawah_amount_discount/objects/<model("atawah_amount_discount.atawah_amount_discount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('atawah_amount_discount.object', {
#             'object': obj
#         })
