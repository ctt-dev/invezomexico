# -*- coding: utf-8 -*-
# from odoo import http


# class Autofacturacion(http.Controller):
#     @http.route('/autofacturacion/autofacturacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/autofacturacion/autofacturacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('autofacturacion.listing', {
#             'root': '/autofacturacion/autofacturacion',
#             'objects': http.request.env['autofacturacion.autofacturacion'].search([]),
#         })

#     @http.route('/autofacturacion/autofacturacion/objects/<model("autofacturacion.autofacturacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('autofacturacion.object', {
#             'object': obj
#         })
