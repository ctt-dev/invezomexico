# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.tools.image import image_data_uri
# from urllib.parse import urlencode
# from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
import logging
_logger = logging.getLogger(__name__)

class ProductCategoryAttribute(models.Model):
    _name = "product.category.attribute"
    _description = "Lineas de plantilla para Mercado Libre"

    product_id = fields.Many2one('product.template', string="Producto")
    categ_id = fields.Many2one("mercadolibre.category", related="product_id.meli_categ_id")
    attr_id = fields.Many2one("mercadolibre.attribute", string="Atributo")
    value = fields.Char(string="Valor")

class CTTMLProductTmplate(models.Model):
    _inherit = 'product.template'
    _description = 'Atributos y funciones para Mercado Libre'

    meli_categ_id = fields.Many2one("mercadolibre.category", string="Categoria de Mercado Libre")
    meli_categ_attribute_ids = fields.One2many(
        "product.category.attribute",
        "product_id",
        string="Atributos de categoria"
    )
    
    # mercadolibre_category_id = fields.Char(string="Categoria de Mercado Libre")
    # mercadolibre_price = fields.Char(string="Precio en mercado Libre")
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
    mercadolibre_warranty = fields.Integer(string='Garantía', help='Garantía del producto. Es obligatorio y debe ser un número seguido por una unidad temporal. Ej. 2 meses, 3 años.')
    mercadolibre_warranty_unit = fields.Selection(
        [("días","Días"),
         ("meses","Meses"),
         ("años","Años")],
        string="Unidad de garantia"
    )

    # #ATRIBUTOS OBLIGATORIOS
    # mercadolibre_BRAND = fields.Char(string="Marca")
    # mercadolibre_MODEL = fields.Char(string="Modelo")
    # mercadolibre_LOAD_INDEX = fields.Char(string="Índice de carga")
    # mercadolibre_TIRES_NUMBER = fields.Char(string="Cantidad de llantas")
    # mercadolibre_AUTOMOTIVE_TIRE_ASPECT_RATIO = fields.Char(string="Relación de aspecto")
    # mercadolibre_SECTION_WIDTH = fields.Char(string="Ancho de sección")
    # mercadolibre_RIM_DIAMETER = fields.Char(string="Diámetro del rin")

    # #ATRIBUTOS DE INVENXO
    # mercadolibre_LOAD_RANGE = fields.Char(string="Rango de carga")
    # mercadolibre_TERRAIN_TYPE = fields.Char(string="Tipo de terreno")
    # mercadolibre_TIRE_CONSTRUCTION_TYPE = fields.Char(string="Tipo de construcción")
    # mercadolibre_UNIT_TYPE = fields.Char(string="Tipo de unidad")
    # mercadolibre_IS_RUN_FLAT = fields.Char(string="Es run flat")

    def _import_ml_catgory(self,category_id):
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')

        api_conector = MeliApi({'access_token': access_token})

        category_obj = self.env["mercadolibre.category"]
        ml_cat_id = category_obj.search([('meli_id','=',category_id)],limit=1)

        if not ml_cat_id:
            url = "/categories/"+category_id
            response = api_conector.get(path=url)
            data = response.json()

            ml_cat_id = category_obj.create({
                'meli_id': data['id'],
                'name': data['name']})

            return ml_cat_id

        return False
    
    def predict_category(self):
        self.ensure_one()

        params = self.env['ir.config_parameter'].sudo()
        site_id = params.get_param('ctt_mercado_libre.mercado_libre_site_id')
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
        
        url = "/sites/"+site_id+"/domain_discovery/search?q="+self.name

        api_conector = MeliApi({'access_token': access_token})
        response = api_conector.get(path=url)

        data = response.json()
        category_id = data[0]['category_id']

        ml_cat_id = self._import_ml_catgory(category_id)

        if ml_cat_id:
            self.write({'meli_categ_id': ml_cat_id.id})
            
        
    def import_category(self):
        self.ensure_one()
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')

        url = "/categories/"+self.mercadolibre_category_id+"/technical_specs/input"

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
    
    def publicar_producto(self):
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
        base_url = params.get_param('web.base.url')
        image_url_1920 = base_url + '/web/image?' + 'model=product.template&id=' + str(self.id) + '&field=image_1920'
        url = "/items/"
        _logger.warning(url)

        api_conector = MeliApi({'access_token': access_token})

        body = {
            "title": self.name + " - Test - No ofertar",
            "category_id": self.mercadolibre_category_id,
            "price": self.list_price,
            "currency_id": "MXN",
            "available_quantity": 1,
            "buying_mode": self.mercadolibre_buying_mode,
            "condition": self.mercadolibre_condition,
            "listing_type_id": self.mercadolibre_listing_type,
            "sale_terms":[
                {"id":"WARRANTY_TYPE",
                "value_name": self.mercadolibre_warranty_type},
                {"id":"WARRANTY_TIME",
                "value_name": self.mercadolibre_warranty}],
            "pictures":[
                {"source": image_url_1920}],
            "attributes":[
                {"id":"BRAND",
                 "value_name": self.mercadolibre_BRAND,
                 "value_id": "995"
                },
                {"id":"MODEL",
                 "value_name": self.mercadolibre_MODEL},
                {"id":"LOAD_INDEX",
                 "value_name": self.mercadolibre_LOAD_INDEX},
                {"id":"TIRES_NUMBER",
                 "value_name": self.mercadolibre_TIRES_NUMBER},
                {
                    "id":"AUTOMOTIVE_TIRE_ASPECT_RATIO",
                     "value_name": self.mercadolibre_AUTOMOTIVE_TIRE_ASPECT_RATIO
                },
                {"id":"SECTION_WIDTH",
                 "value_name": self.mercadolibre_SECTION_WIDTH},
                {"id":"RIM_DIAMETER",
                 "value_name": self.mercadolibre_RIM_DIAMETER},
            ]
        }

        response = api_conector.post(path=url, body=body)
        data = response.json()
            

        