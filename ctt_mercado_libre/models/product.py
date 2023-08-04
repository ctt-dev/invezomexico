# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.parse import urlencode
from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
import logging
_logger = logging.getLogger(__name__)

class CTTMLProductTmplate(models.Model):
    _inherit = 'product.template'
    _description = 'Atributos y funciones para Mercado Libre'

    mercadolibre_category_id = fields.Char(string="Categoria de Mercado Libre")
    mercadolibre_price = fields.Char(string="Precio en mercado Libre")
    mercadolibre_buying_mode = fields.Selection(
        [("buy_it_now","Compre ahora"),
         ("classified","Clasificado")],
        string='Método de compra predeterminado',
        default="buy_it_now")
    mercadolibre_condition = fields.Selection(
        [("new", "Nuevo"),
        ("used", "Usado"),
        ("not_specified","No especificado")],
        string='Condición',
        default="new")
    mercadolibre_listing_type = fields.Selection(
        [("free","Libre"),
        ("bronze","Bronce/Clásica-(UY)"),
        ("silver","Plata"),
        ("gold","Oro"),
        ("gold_premium","Gold Premium/Oro Premium"),
        ("gold_special","Gold Special/Clásica/Premium-(UY)"),
        ("gold_pro","Oro Pro")],
        string='Tipo de lista',
        help='Tipo de lista  predeterminada para todos los productos')
    mercadolibre_warranty_type = fields.Selection(
        [("Garantía del vendedor","Garantía del vendedor"),
         ("Garantía de fábrica","Garantía de fábrica"),
         ("Sin garantía","Sin garantía")],
        string="Tipo de garantia"
    )
    mercadolibre_warranty = fields.Char(string='Garantía', size=256, help='Garantía del producto. Es obligatorio y debe ser un número seguido por una unidad temporal. Ej. 2 meses, 3 años.')

    #ATRIBUTOS OBLIGATORIOS
    mercadolibre_BRAND = fields.Char(string="Marca")
    mercadolibre_MODEL = fields.Char(string="Modelo")
    mercadolibre_LOAD_INDEX = fields.Char(string="Índice de carga")
    mercadolibre_TIRES_NUMBER = fields.Char(string="Cantidad de llantas")
    mercadolibre_AUTOMOTIVE_TIRE_ASPECT_RATIO = fields.Char(string="Relación de aspecto")
    mercadolibre_SECTION_WIDTH = fields.Char(string="Ancho de sección")
    mercadolibre_RIM_DIAMETER = fields.Char(string="Diámetro del rin")

    #ATRIBUTOS DE INVENXO
    mercadolibre_LOAD_RANGE = fields.Char(string="Rango de carga")
    mercadolibre_TERRAIN_TYPE = fields.Char(string="Tipo de terreno")
    mercadolibre_TIRE_CONSTRUCTION_TYPE = fields.Char(string="Tipo de construcción")
    mercadolibre_UNIT_TYPE = fields.Char(string="Tipo de unidad")
    mercadolibre_IS_RUN_FLAT = fields.Char(string="Es run flat")

    def _import_ml_catgory(self):
        pass
    
    def predict_category(self):
        self.ensure_one()

        params = self.env['ir.config_parameter'].sudo()
        site_id = params.get_param('ctt_mercado_libre.mercado_libre_site_id')
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
        # _logger.warning(site_id)
        # _logger.warning(self.name)
        
        url = "/sites/"+site_id+"/domain_discovery/search?q="+self.name
        # _logger.warning(url)

        api_conector = MeliApi({'access_token': access_token})
        response = api_conector.get(path=url)
        # _logger.warning(response)
        # _logger.warning(response.json())

        data = response.json()

        self.write({
            'mercadolibre_category_id': data[0]['category_id']
        })
        
    def import_category(self):
        self.ensure_one()
        _logger.warning("Importando atributos")
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')

        url = "/categories/"+self.mercadolibre_category_id+"/technical_specs/input"
        _logger.warning(url)

        api_conector = MeliApi({'access_token': access_token})
        response = api_conector.get(path=url)
        data = response.json()

        # _logger.warning(data['groups'][0])
        # _logger.warning("Main")
        # for component in data['groups'][0]['components']:
        #     _logger.warning(component['attributes'][0]['id'])
        #     _logger.warning(component['attributes'][0]['tags'])
        # _logger.warning("PRODUCT_REGISTRIES")
        # for component in data['groups'][1]['components']:
        #     _logger.warning(component['attributes'][0]['id'])
        #     _logger.warning(component['attributes'][0]['tags'])
        # _logger.warning("OTHER")
        # for component in data['groups'][2]['components']:
        #     _logger.warning(component['attributes'][0]['id'])
        #     _logger.warning(component['attributes'][0]['tags'])

        for group in data['groups']:
            _logger.warning(group['id'])
            for component in group['components']:
                if 'required' in component['attributes'][0]['tags']:
                    _logger.warning(component['attributes'][0]['id'])
            

        