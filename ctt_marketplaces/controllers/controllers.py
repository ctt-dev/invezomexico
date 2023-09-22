# -*- coding: utf-8 -*-
# from odoo import http


# class CttMarketplaces(http.Controller):
#     @http.route('/ctt_marketplaces/ctt_marketplaces', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ctt_marketplaces/ctt_marketplaces/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ctt_marketplaces.listing', {
#             'root': '/ctt_marketplaces/ctt_marketplaces',
#             'objects': http.request.env['ctt_marketplaces.ctt_marketplaces'].search([]),
#         })

#     @http.route('/ctt_marketplaces/ctt_marketplaces/objects/<model("ctt_marketplaces.ctt_marketplaces"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ctt_marketplaces.object', {
#             'object': obj
#         })
