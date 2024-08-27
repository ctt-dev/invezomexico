# -*- coding: utf-8 -*-
# from odoo import http


# class AdroneConfig(http.Controller):
#     @http.route('/adrone_config/adrone_config', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/adrone_config/adrone_config/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('adrone_config.listing', {
#             'root': '/adrone_config/adrone_config',
#             'objects': http.request.env['adrone_config.adrone_config'].search([]),
#         })

#     @http.route('/adrone_config/adrone_config/objects/<model("adrone_config.adrone_config"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('adrone_config.object', {
#             'object': obj
#         })
