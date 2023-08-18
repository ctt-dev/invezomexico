# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
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
    attr_units = fields.Many2many("mercadolibre.units", related="attr_id.unit_ids")
    has_value = fields.Boolean(related="attr_id.has_values")
    value = fields.Char(string="Valor")
    value_id = fields.Many2one("mercadolibre.value", string="Valores predeterminados")
    unit_id = fields.Many2one("mercadolibre.units", string="Unidad")
    

class CTTMLProductTmplate(models.Model):
    _inherit = 'product.template'
    _description = 'Atributos y funciones para Mercado Libre'

    meli_id = fields.Char(string="ID en Mercado Libre")
    meli_categ_id = fields.Many2one("mercadolibre.category", string="Categoria de Mercado Libre")
    mercadolibre_title = fields.Char(string="Titulo", size=60)
    mercadolibre_description = fields.Text(string="Descripción en Mercado Libre")
    meli_categ_attribute_ids = fields.One2many(
        "product.category.attribute",
        "product_id",
        string="Atributos de categoria"
    )
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
    mercadolibre_local_pick_up = fields.Boolean(default=False, string="Retiro en persona")
    mercadolibre_free_shipping = fields.Boolean(default=False, string="Envio gratis")
    mercadolibre_store_pick_up = fields.Boolean(default=False, string="Retiro en sucursal")
    mercado_shipping_mode = fields.Selection(
        [("me2","Mercado Envios 2"),
         ("not_specified", "No especificado")],
        string="Modo de envio",
        default="me2"
    )

    def _import_ml_catgory(self,category_id):
        category_obj = self.env["mercadolibre.category"]
        ml_cat_id = category_obj.search([('meli_id','=',category_id)],limit=1)
        if not ml_cat_id:
            params = self.env['ir.config_parameter'].sudo()
            access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
    
            api_conector = MeliApi({'access_token': access_token})

            url = "/categories/"+category_id
            response = api_conector.get(path=url)
            data = response.json()

            ml_cat_id = category_obj.create({
                'meli_id': data['id'],
                'name': data['name']})

        return ml_cat_id

        # return False
    
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
    
    def publicar_producto(self):
        self.ensure_one()
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
        currency = params.get_param("ctt_mercado_libre.mercado_libre_currency_id")
        base_url = params.get_param('web.base.url')
        image_url_1920 = base_url + '/web/image?' + 'model=product.template&id=' + str(self.id) + '&field=image_1920'
        url = "/items/"

        api_conector = MeliApi({'access_token': access_token})

        attributes = []

        for line in self.meli_categ_attribute_ids:
            data = {"id": line.attr_id.meli_id}

            if line.attr_id.has_values:
                data["value_name"] = line.value_id.name
                data["value_id"] = line.value_id.meli_id
            else:
                data["value_name"] = line.value if line.attr_id.type == "string" else "%s %s" % (line.value, line.unit_id.name)
            
            attributes.append(data)
        
        body = {
            "title": self.mercadolibre_title,
            "category_id": self.meli_categ_id.meli_id,
            "price": self.list_price,
            "currency_id": currency,
            "available_quantity": 1,
            "buying_mode": self.mercadolibre_buying_mode,
            "condition": self.mercadolibre_condition,
            "listing_type_id": self.mercadolibre_listing_type,
            "sale_terms":[
                {"id":"WARRANTY_TYPE",
                "value_name": self.mercadolibre_warranty_type},
                {"id":"WARRANTY_TIME",
                "value_name": "%s %s" % (self.mercadolibre_warranty, self.mercadolibre_warranty_unit) }],
            "pictures":[
                {"source": image_url_1920}],
            "attributes": attributes,
            "shipping": {
                "mode": self.mercado_shipping_mode,
                "local_pick_up": self.mercadolibre_local_pick_up,
                "free_shipping": self.mercadolibre_free_shipping,
                "methods": [],
                "dimensions": None,
                "tags": [],
                "logistic_type": "not_specified",
                "store_pick_up": self.mercadolibre_store_pick_up
            }
        }

        for image in self.product_template_image_ids:
            body["pictures"].append({
                "source": base_url + '/web/image?' + 'model=product.image&id=' + str(image.id) + '&field=image_1920'
            })
        
        response = api_conector.post(path=url, body=body)
        data = response.json()
        if 'error' in data:
            message = ""
            for item in data['cause']:
                message += item["message"] + "\n"
            raise ValidationError(message)
        
        self.write({"meli_id": data["id"]})

        if self.mercadolibre_description:
            url = "/items/"+self.meli_id+"/description"
            body = {'plain_text': self.mercadolibre_description}
    
            response = api_conector.put(path=url, body=body)
            data = response.json()
            if 'error' in data:
                message = ""
                for item in data['cause']:
                    message += item["message"] + "\n"
                raise ValidationError(message)  
        else:
            raise ValidationError("Es necesaria una descripción del producto")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'sticky': False,
                'message': ("Artículo publicado en Mercado Libre"),
            }
        }
    def import_product(self):
        self.ensure_one()
        self.meli_categ_attribute_ids = False
        params = self.env['ir.config_parameter'].sudo()
        site_id = params.get_param("ctt_mercado_libre.mercado_libre_site_id")
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')
        if not self.meli_id or self.meli_id[:3] != site_id:
            raise ValidationError("ID de Mercado Libre con formato %sXXXXXXXXXX" % (site_id))

        url = "/items/"+self.meli_id

        api_conector = MeliApi({'access_token': access_token})
        response = api_conector.get(path=url)

        data = response.json()
        if 'error' in data:
            message = ""
            for item in data['cause']:
                message += item["message"] + "\n"
            raise ValidationError(message)

        ml_cat_id = self._import_ml_catgory(data["category_id"])
        
        vals = {
            "meli_categ_id": ml_cat_id.id,
            "mercadolibre_title": data["title"],
            "mercadolibre_buying_mode": data["buying_mode"],
            "mercadolibre_condition": data["condition"],
            "mercadolibre_listing_type": data["listing_type_id"],
            
        }

        if "sale_terms" in data:
            for item in data["sale_terms"]:
                if item["id"] == "WARRANTY_TYPE":
                    vals["mercadolibre_warranty_type"] = item["value_name"]
                if item["id"] == "WARRANTY_TIME":
                    vals["mercadolibre_warranty"] = item["value_struct"]["number"]
                    vals["mercadolibre_warranty_unit"] = item["value_struct"]["unit"]

        #Atributos
        attr_lines = self.env["product.category.attribute"]
        attr_obj = self.env["mercadolibre.attribute"]
        for attr in data["attributes"]:
            attr_id = attr_obj.search([("categ_id.meli_id","=",data["category_id"]),("meli_id","=",attr["id"])])

            prod_attr_vals = {
                "product_id": self.id,
                "categ_id": self.meli_categ_id.id,
                "attr_id": attr_id.id,
            }

            if attr_id.has_values:
                prod_attr_vals["value_id"] = self.env["mercadolibre.value"].search([("attr_id","=",attr_id.id),("name","=",attr["value_name"])]).id
            if not attr_id.has_values and attr_id.type != "number_unit":
                prod_attr_vals["value"] = attr["value_name"]
            elif not attr_id.has_values and attr_id.type == "number_unit":
                prod_attr_vals["value"] = attr["value_struct"]["number"]
                prod_attr_vals["unit_id"] = self.env["mercadolibre.units"].search([("name","=",attr["value_struct"]["unit"])]).id

            attr_lines += self.env["product.category.attribute"].create(prod_attr_vals)

        vals["meli_categ_attribute_ids"] = attr_lines.ids
        
        #Envios
        if "shipping" in data:
            vals["mercado_shipping_mode"] = data["shipping"]["mode"]
            vals["mercadolibre_local_pick_up"] = data["shipping"]["local_pick_up"]
            vals["mercadolibre_free_shipping"] = data["shipping"]["free_shipping"]
            vals["mercadolibre_store_pick_up"] = data["shipping"]["store_pick_up"]

        #Descripcion
        url = "/items/"+self.meli_id+"/description"
        response = api_conector.get(path=url)
        data = response.json()

        vals["mercadolibre_description"] = data["plain_text"]
        
        self.write(vals)