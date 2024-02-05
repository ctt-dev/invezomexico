from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class MyController(http.Controller):
    @http.route('/TomarValoresSelect',  auth='public')
    def mi_funcion(self, **kw):
        anchos_value = post.get('anchos_select')
        series_value = post.get('series_select')
        diametros_value = post.get('diametros_select')
        _logger.warning(anchos_value)
        _logger.warning(series_value)
        _logger.warning(diametros_value)
        
        # Hacer lo que necesites con los valores seleccionados
        # return http.request.make_response("Valores impresos en la consola")
        # return http.request.render('website.homepage', {
        #     'anchos_value': anchos_value,
        #     'series_value': series_value,
        #     'diametros_value': diametros_value,
        # })
        return http.request.make_response("Valor impreso en la consola")

    @http.route('/TomarValoresSelectP', auth='public')
    def mi_funcion(self, **kw):
        # _logger.warning(self)
        # _logger.warning(kw)
        # _logger.warning('OIAHDOIASOIDASODKKJ')
        anchos_value = kw['anchos_select']
        series_value = kw['series_select']
        diametros_value = kw['diametros_select']
        _logger.warning(anchos_value)
        _logger.warning(series_value)
        _logger.warning(diametros_value)

        # product_ids = request.env['product.template'].search([('rin','=',diametros_value),('ancho','=',anchos_value),('indice_carga','=',series_value)])

        # cadena = ""

        # for product in product_ids:
        #     cadena = cadena + product.name + ", "

        # Hacer lo que necesites con el valor seleccionado
        # return http.request.make_response(cadena)
        return request.redirect(f'/shop?rin={diametros_value}&ancho={anchos_value}&indice_carga={series_value}')
