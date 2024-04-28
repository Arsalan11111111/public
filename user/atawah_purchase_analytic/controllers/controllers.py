# -*- coding: utf-8 -*-
# from odoo import http


# class AtawahPurchaseAnalytic(http.Controller):
#     @http.route('/atawah_purchase_analytic/atawah_purchase_analytic', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/atawah_purchase_analytic/atawah_purchase_analytic/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('atawah_purchase_analytic.listing', {
#             'root': '/atawah_purchase_analytic/atawah_purchase_analytic',
#             'objects': http.request.env['atawah_purchase_analytic.atawah_purchase_analytic'].search([]),
#         })

#     @http.route('/atawah_purchase_analytic/atawah_purchase_analytic/objects/<model("atawah_purchase_analytic.atawah_purchase_analytic"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('atawah_purchase_analytic.object', {
#             'object': obj
#         })
