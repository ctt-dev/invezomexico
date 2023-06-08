# -*- coding: utf-8 -*-
# from odoo import http


# class LlantasConfig(http.Controller):
#     @http.route('/llantas_config/llantas_config', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/llantas_config/llantas_config/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('llantas_config.listing', {
#             'root': '/llantas_config/llantas_config',
#             'objects': http.request.env['llantas_config.llantas_config'].search([]),
#         })

#     @http.route('/llantas_config/llantas_config/objects/<model("llantas_config.llantas_config"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('llantas_config.object', {
#             'object': obj
#         })
