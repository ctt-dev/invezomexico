# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from urllib.parse import urlencode
# from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
import json
import logging
_logger = logging.getLogger(__name__)

class MercadoLibreCategoryImport(models.TransientModel):
    _name = "mercadolibre.category.import"
    _description = "Wizard de Importacion de Categoria desde MercadoLibre"

    mercadolibre_id = fields.Char(string="MercadoLibre ID")
    name = fields.Char(string="Nombre")

class MercadoLibreCategory(models.Model):
    _name = "mercadolibre.category"
    _description = "Categorias de Mercado Libre"

    meli_id = fields.Char(string="MercadoLibre ID")
    name = fields.Char(string="Nombre")
    attribute_ids = fields.One2many(
        "mercadolibre.attribute",
        "categ_id",
        string="Atributos de categoria"
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MercadoLibreCategory, self).create(vals_list)

        res._import_attributes()
        return res

    def _import_attributes(self):
        params = self.env['ir.config_parameter'].sudo()
        access_token = params.get_param('ctt_mercado_libre.mercado_libre_token')

        url = "/categories/"+self.meli_id+"/attributes"

        api_conector = MeliApi({'access_token': access_token})
        response = api_conector.get(path=url)
        data = response.json()

        for categ_attr in data:

            _logger.warning(categ_attr['tags'])

            attr_data = {
                "categ_id": self.id,
                "meli_id": categ_attr["id"],
                "name": categ_attr["name"],
                "required": ('catalog_required' in categ_attr['tags']) or ('required' in categ_attr['tags'])
            }

            if ('values' in categ_attr):
                attr_data['values'] = json.dumps(categ_attr['values'])
            
            if ('value_type' in categ_attr):
                attr_data['type'] = categ_attr['value_type']
            
            attribute = self.env["mercadolibre.attribute"].create(attr_data)

class MercadoLibreAttribute(models.Model):
    _name = "mercadolibre.attribute"
    _description = "Atributo de categoria"

    categ_id = fields.Many2one("mercadolibre.category", string="Categoria")
    meli_id = fields.Char(string="ID de Mercado Libre")
    name = fields.Char(string="Nombre")
    required = fields.Boolean(string="Requerido",default=False)
    values = fields.Text(string="Values")
    type = fields.Char(string="Type")
