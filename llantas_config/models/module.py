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

    sale_id=fields.Many2one(
        "sale.order",
        string="Venta",
        store=True,
    )
    
    name=fields.Char(
        related="sale_id.name",
        string="Nombre",
        tracking=True
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        related="sale_id.comprador_id",
        string="Comprador",
        tracking=True,
        company_dependent=True,
    )

    # venta=fields.Char(
    #     string="Venta",
    #     tracking=True
    # )
    
    # cliente=fields.Char(
        
    #     string="Cliente",
    #     tracking=True
    # )    

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
    
    # status = fields.Many2one(
    #     'llantas_config.status', 
    #     string="Status",
    # )

    status = fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),],
        related="sale_id.ventas_status",
        string="Status",
    )
    
    fecha=fields.Datetime(
        related="sale_id.fecha_venta",
        string="Fecha",    
        tracking=True,
    )
    
    dias=fields.Integer(
        string="Dias",
    )

    comentarios=fields.Char(
        string="Comentarios",
        tracking=True
    )

    orden_entrega=fields.Many2one(
        "stock.picking",
        string="Orden de entrega",
    )

    link_venta=fields.Char(
        related="sale_id.link_venta",
        string="Link venta",
    )

    no_venta=fields.Char(
        related="sale_id.folio_venta",
        string="No. Venta",
    )

    comision=fields.Float(
        string="Comisión",
    )

    envio=fields.Float(
        string="Envio",
    )

    company_id=fields.Many2one(
        "res.company",
        related="sale_id.company_id",
        string="Empresa",
    )
    