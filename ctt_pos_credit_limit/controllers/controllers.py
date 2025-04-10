# -*- coding: utf-8 -*-
# from odoo import http


# class CttPosCreditLimit(http.Controller):
#     @http.route('/ctt_pos__credit_limit/ctt_pos__credit_limit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ctt_pos__credit_limit/ctt_pos__credit_limit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ctt_pos__credit_limit.listing', {
#             'root': '/ctt_pos__credit_limit/ctt_pos__credit_limit',
#             'objects': http.request.env['ctt_pos__credit_limit.ctt_pos__credit_limit'].search([]),
#         })

#     @http.route('/ctt_pos__credit_limit/ctt_pos__credit_limit/objects/<model("ctt_pos__credit_limit.ctt_pos__credit_limit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ctt_pos__credit_limit.object', {
#             'object': obj
#         })
