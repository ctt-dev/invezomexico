# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from urllib.parse import urlencode
# from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
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

    mercadolibre_id = fields.Char(string="MercadoLibre ID")
    name = fields.Char(string="Nombre")

class MercadoLibreAttribute(models.Model):
    _name = "mercadolibre.attribute"
    _description = "Atributo de categoria"

    categ_id = fields.Many2one("mercadolibre.category", string="Categoria")
    meli_id = fields.Char(string="ID de Mercado Libre")
    name = fields.Char(string="Nombre")
    required = fields.Boolean(string="Requerido",default=False)
