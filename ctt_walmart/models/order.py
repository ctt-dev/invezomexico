# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from odoo.addons.ctt_walmart.utils.WalmartAPI import WalmartAPI
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    # _description = 'Modelo para seguimiento de ordenes de walmart'

    # data = fields.Text(string="data")

    def search_new_orders(self):
        _logger.warning(f"Buscando ordenes")
        #Inicializar Clinte de Walmart
        params = self.env['ir.config_parameter'].sudo()
        client_id = params.get_param('ctt_walmart.walmart_client_id')
        client_secret = params.get_param('ctt_walmart.walmart_client_secret')

        api_client = WalmartAPI(client_id, client_secret)

        url = f"orders" #Endpoint

        params = {
            "statusCodeFilter": "Created",
            "createdStartDate": "2023-11-06T00:00:00.000-06:00",
            "createdEndDate": "2023-11-06T23:59:59.000-06:00",
        }

        try:
            response = api_client.send_request("GET", url, params=params) #Request GET
            # _logger.warning(response)

            for order in response["order"]:
                _logger.warning(f"Fecha: {order['orderDate']}")

            response_data = json.dumps(response)
        except Exception as e:
            # _logger.warning(f"feedId: {self.feedId}")
            _logger.warning(f"Ocurrió un error inesperado: {e}")