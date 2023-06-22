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

    name= fields.Char(
        string="Nombre",
    )

    comprador=fields.Char(
        string="Comprador",
    )
    
    venta=fields.Char(
        string="Venta",
    )
    
    cliente=fields.Char(
        string="Cliente",
    )
    
    marketplace=fields.Char(
        string="Marketplace",
    )
    
    proveedor=fields.Char(
        string="Proveedor",
    )
    
    registro=fields.Boolean(
        string="Registro",
        
    )
    orden_compra=fields.Char(
        string="Orden de compra",
    )
    guia=fields.Char(
        string="No. Guia",
        
    )
    no_recoleccion=fields.Char(
        string="No. Recoleccion",    
    )
    
    status_enviado=fields.Boolean(
        string="Status"
    )
    
    factura_prov=fields.Char(
        string="Factura proveedor",
    )
    
    num_cliente=fields.Char(
        string="Num. Cliente",
    )
    
    factura_cliente=fields.Char(
        string="Factura cliente",
    )
    status = fields.Many2one(
        'llantas_config.status', 
        string="Status")
    
    fecha=fields.Datetime(
        string="Fecha",    
    )
    
    dias=fields.Integer(
        string="Dias",
    )