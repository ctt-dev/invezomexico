# -*- coding: utf-8 -*-
# from odoo import http


# class CttMercadoLibre(http.Controller):
#     @http.route('/ctt_mercado_libre/ctt_mercado_libre', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ctt_mercado_libre/ctt_mercado_libre/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ctt_mercado_libre.listing', {
#             'root': '/ctt_mercado_libre/ctt_mercado_libre',
#             'objects': http.request.env['ctt_mercado_libre.ctt_mercado_libre'].search([]),
#         })

#     @http.route('/ctt_mercado_libre/ctt_mercado_libre/objects/<model("ctt_mercado_libre.ctt_mercado_libre"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ctt_mercado_libre.object', {
#             'object': obj
#         })
