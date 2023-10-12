# -*- coding: utf-8 -*-
# from odoo import http


# class CttWalmart(http.Controller):
#     @http.route('/ctt_walmart/ctt_walmart', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ctt_walmart/ctt_walmart/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ctt_walmart.listing', {
#             'root': '/ctt_walmart/ctt_walmart',
#             'objects': http.request.env['ctt_walmart.ctt_walmart'].search([]),
#         })

#     @http.route('/ctt_walmart/ctt_walmart/objects/<model("ctt_walmart.ctt_walmart"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ctt_walmart.object', {
#             'object': obj
#         })
