from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  

class marketplace_product(models.Model):
    _name = 'llantas_config.product_marketplace'
    _description = 'Marketplace producto'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string="Nombre",
    )

    product_ids=fields.Many2one(
        "product.template",
        string="Producto",
    )

    sku=fields.Char(
        string="SKU",
    )

    color = fields.Integer(
        string="Color",
        required=True
    )

    sku_premium=fields.Char(
        string="SKU Premium",
    )

    sku_paquete_clasico=fields.Char(
        string="SKU paquete clasico",
    )

    sku_paquete_premium=fields.Char(
        string="SKU paquete premium",
    )

    codigo_clasico=fields.Char(
        string="Codigo clasico",
    )
    
    codigo_premium=fields.Char(
        string="Codigo clasico",
    )

    codigo_paquete_clasico=fields.Char(
        string="Codigo clasico",
    )

    codigo_paquete_premium=fields.Char(
        string="Codigo clasico",
    )

    codigo_ean=fields.Char(
        string="Codigo de barras",
    )
    
    
    