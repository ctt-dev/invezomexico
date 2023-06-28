# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_llantas"
    _description = "Llantas"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name= fields.Char(
        string="Nombre",
        tracking=True
    )

    comprador=fields.Char(
        string="Comprador",
        tracking=True
    )
    
    venta=fields.Char(
        string="Venta",
        tracking=True
    )
    
    cliente=fields.Char(
        string="Cliente",
        tracking=True
    )
    
    marketplace=fields.Char(
        string="Marketplace",
        tracking=True
    )
    
    proveedor=fields.Char(
        string="Proveedor",
        tracking=True
    )
    
    registro=fields.Boolean(
        string="Registro",
        tracking=True
        
    )
    orden_compra=fields.Char(
        string="Orden de compra",
        tracking=True
    )
    guia=fields.Char(
        string="No. Guia",
        tracking=True
        
    )
    no_recoleccion=fields.Char(
        string="No. Recoleccion",  
        tracking=True
    )
    
    status_enviado=fields.Boolean(
        string="Status",
        tracking=True
    )
    
    factura_prov=fields.Char(
        string="Factura proveedor",
        tracking=True
    )
    
    num_cliente=fields.Char(
        string="Num. Cliente",
        tracking=True
    )
    
    factura_cliente=fields.Char(
        string="Factura cliente",
        tracking=True
    )
    status = fields.Many2one(
        'llantas_config.status', 
        string="Status",
    tracking=True
    )
    
    fecha=fields.Datetime(
        string="Fecha",    
        tracking=True
    )
    
    dias=fields.Integer(
        string="Dias",
        tracking=True
    )

    comentarios=fields.Char(
        string="Comentarios",
        tracking=True
    )