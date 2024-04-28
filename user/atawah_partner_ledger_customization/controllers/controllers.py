# -*- coding: utf-8 -*-
# from odoo import http


# class AtawahPartnerLedgerCustomization(http.Controller):
#     @http.route('/atawah_partner_ledger_customization/atawah_partner_ledger_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/atawah_partner_ledger_customization/atawah_partner_ledger_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('atawah_partner_ledger_customization.listing', {
#             'root': '/atawah_partner_ledger_customization/atawah_partner_ledger_customization',
#             'objects': http.request.env['atawah_partner_ledger_customization.atawah_partner_ledger_customization'].search([]),
#         })

#     @http.route('/atawah_partner_ledger_customization/atawah_partner_ledger_customization/objects/<model("atawah_partner_ledger_customization.atawah_partner_ledger_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('atawah_partner_ledger_customization.object', {
#             'object': obj
#         })
