# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from odoo.addons.ctt_walmart.utils.WalmartAPI import WalmartAPI
import logging
_logger = logging.getLogger(__name__)

class CttWalmartConfigSettings(models.Model):
    _name = 'walmart.feed'
    _description = 'Modelo para seguimiento de peticiones a walmart'

    feedId = fields.Char(string='ID de petición')
    status = fields.Selection(selection=[
        ('RECEIVED','Enviado'),
        ('INPROGRESS','En progreso'),
        ('PROCESSED','Procesada'),
        ('ERROR', 'Error')
        ],string='Estado')
    data = fields.Text(string='Información')
    # template_id = fields.Many2one('marketplaces.template', string='Plantilla')

    def feed_status(self):
        self.ensure_one()

        #Inicializar Clinte de Walmart
        params = self.env['ir.config_parameter'].sudo()
        client_id = params.get_param('ctt_walmart.walmart_client_id')
        client_secret = params.get_param('ctt_walmart.walmart_client_secret')

        api_client = WalmartAPI(client_id, client_secret)

        url = f"feeds/{self.feedId}?includeDetails=true" #Endpoint

        try:
            response = api_client.send_request("GET", url) #Request GET
            _logger.warning(response)

            response_data = json.dumps(response)
            #Sobrescribir status
            self.write({
                'status': response['feedStatus'],
                'data': response_data
            })

        except Exception as e:
            _logger.warning(f"feedId: {self.feedId}")
            _logger.warning(f"Ocurrió un error inesperado: {e}")

    def cron_feed_status(self):
        feed_list = self.env['walmart.feed'].search([('status','in',['RECEIVED','INPROGRESS'])])

        for feed in feed_list:
            feed.feed_status()