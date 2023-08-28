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
        tracking=True,
    )
    
    product_ids=fields.Many2one(
        "product.template",
        string="Producto",
        tracking=True,
    )
    
    sku=fields.Char(
        string="SKU",
    )

    color = fields.Integer(
        string="Color",
        tracking=True,
    )

    sku_premium=fields.Char(
        string="SKU Premium",
    )

    sku_paquete_clasico=fields.Char(
        string="SKU paquete clasico",
    )

    
    codigo_clasico=fields.Char(
        string="Codigo individual clasico",
        tracking=True,
    )
    codigo_premium=fields.Char(
        string="Codigo individual premium",
        tracking=True,
    )
    codigo_paquete_clasico=fields.Char(
        string="Codigo paquete clasico",
        tracking=True,
    )   
    codigo_paquete_premium=fields.Char(
        string="Codigo paquete premium",
        tracking=True,
    )
    id_clasico=fields.Char(
        string="ID individual clasico",
        tracking=True,
    )
    id_premium=fields.Char(
        string="ID individual premium",
        tracking=True,
    )
    id_paquete_clasico=fields.Char(
        string="ID paquete clasico",
        tracking=True,
    )   
    id_paquete_premium=fields.Char(
        string="ID paquete premium",
        tracking=True,
    )
    sku_individual=fields.Char(
        string="SKU individual",
        tracking=True,
    )
    sku_paquete=fields.Char(
        string="SKU paquete",
        tracking=True,
    )

    codigo_ean=fields.Char(
        string="EAN-UPC individual",
        tracking=True,
    )
    codigo_ean_paquete=fields.Char(
        string="EAN-UPC paquete",
        tracking=True,
    )

    no_tienda=fields.Char(
        string="No. Tienda",
        tracking=True,
    )

    no_proveedor=fields.Char(
        string="No. Proveedor",
        tracking=True,
    )

    grupo_articulo=fields.Char(
        string="Grupo articulo",
        tracking=True,
    )

    palabra_clave=fields.Char(
        string="Palabra clave",
        tracking=True,
    )

    precio=fields.Float(
        string="Precio",
        tracking=True,
    )
    
    estado_publicacion = fields.Selection([
        ('01','Activo'),
        ('02','Pausada'),
        ('03','Finalizada'),
    ], string="Estado publicación", default='01', tracking=True, store=True)

    condicion = fields.Selection([
        ('01','Nuevo'),
        ('02','Usado'),
    ], string="Condición", default='01', tracking=True, store=True)

    garantia=fields.Char(
        string="Garantia",
        tracking=True,
    )

    tipo_vehiculo=fields.Char(
        string="Tipo vehiculo",
        tracking=True,
    )

    posicion=fields.Char(
        string="Posición",
        tracking=True,
    )
    lado=fields.Char(
        string="Lado",
        tracking=True,
    )

    ano_vehiculo=fields.Integer(
        string="Año vehiculo",
        tracking=True,
    )

    voltaje=fields.Char(
        string="Voltaje",
        tracking=True,
    )

    potencia=fields.Char(
        string="Potencia",
        tracking=True,
    )

    capacidad_produccion=fields.Char(
        string="Capacidad de producción",
        tracking=True,
    )

    capacidad_almacenamiento=fields.Char(
        string="Capacidad de almacenamiento",
        tracking=True,
    )

    forma_hielo=fields.Char(
        string="Forma de hielo",
        tracking=True,
    )

    material=fields.Char(
        string="Material",
        tracking=True,
    )

    category=fields.Char(
        string="Categoria",
        tracking=True,
    )
    
    listado_marketplace = fields.Selection([
        ('01','MERCADOLIBRE'),
        ('02','LIVERPOOL'),
        ('03','COPPEL'),
        ('04','WALMART'),
        ('05','CLAROSHOP'),
        ('06','ELEKTRA'),
        ('07','OTRO'),
    ], string="Listado", default=False, store=True)

    tipo_producto = fields.Selection([
        ('01','LLANTAS'),
        ('02','AMORTIGUADOR'),
        ('03','MAQUINA DE HIELO'),
        ('04','OTRO'),
    ], string="Tipo producto", default=False, store=True)

    categoria = fields.Char(
        string='Categoria',
    )

    garantia = fields.Char(
        string='Garantia',
    )

    image_1920 = fields.Binary(
        string="Imagen",
    )

    peso= fields.Char(
        string="Peso",
    )
    medida= fields.Char(
        string="Medida",
    )
    material= fields.Char(
        string="Material",
    )
    medida_llanta= fields.Char(
        string="Medida llanta",
    )
    medida_rin= fields.Char(
        string="Medida rin",
    )
    marca=fields.Char(
        string="Marca",
    )
    modelo=fields.Char(
        string="Modelo",
    )
    precio_descuento= fields.Float(
        string="Precio de descuento",
    )
    codigo_proveedor= fields.Char(
        string="Código de proveedor",
    )
    