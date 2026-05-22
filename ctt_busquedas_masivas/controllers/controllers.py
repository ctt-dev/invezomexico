# from odoo import http


# class CttBusquedasMasivas(http.Controller):
#     @http.route('/ctt_busquedas_masivas/ctt_busquedas_masivas', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ctt_busquedas_masivas/ctt_busquedas_masivas/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ctt_busquedas_masivas.listing', {
#             'root': '/ctt_busquedas_masivas/ctt_busquedas_masivas',
#             'objects': http.request.env['ctt_busquedas_masivas.ctt_busquedas_masivas'].search([]),
#         })

#     @http.route('/ctt_busquedas_masivas/ctt_busquedas_masivas/objects/<model("ctt_busquedas_masivas.ctt_busquedas_masivas"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ctt_busquedas_masivas.object', {
#             'object': obj
#         })

