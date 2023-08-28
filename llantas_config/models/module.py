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

    comprador_id= fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
        store=True,
    )
    
    comprador=fields.Char(
        string="Comprador",
        tracking=True,
        store=True,
    )

    
    venta=fields.Char(
        string="Venta",
        tracking=True
    )
    
    cliente=fields.Char(
        
        string="Cliente",
        tracking=True
    )
    partner_name=fields.Char(
        related="sale_id.partner_id.name",
        string="Cliente",
        store=True,
    )
    
    marketplace=fields.Char(
        related="sale_id.marketplace.name",
        string="Marketplace",
        tracking=True,
        store=True,
    )

    
    proveedor=fields.Char(
        string="Proveedor",
        tracking=True
    )
    proveedor_id=fields.Many2one(
        "res.partner",
        string="Proveedor",
        tracking=True,
        store=True,
    )
    
    # registro=fields.Boolean(
    #     string="Registro",
    #     tracking=True
        
    # )
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
    
    # status_enviado=fields.Boolean(
    #     string="Status",
    #     tracking=True
    # )
    
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
        tracking=True,
        readonly=True,
    )
    
    dias=fields.Integer(
        string="Dias",
        # tracking=True
    )

    comentarios=fields.Char(
        string="Comentarios",
        tracking=True
    )

    sale_id=fields.Many2one(
        "sale.order",
        string="Venta",
        readonly=True,
        store=True,
    )

    orden_entrega=fields.Many2one(
        "stock.picking",
        string="Orden de entrega",
    )
    