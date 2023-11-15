# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
import logging
import datetime
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_prov"
    _description = "Existencias proveedores"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    proveedor=fields.Many2one(
        "res.partner",
        string="Proveedor",
        tracking=True
    )

    nombre_proveedor=fields.Char(
        related="proveedor.name",
        string="Nombre proveedor",
        tracking=True
        
    )
    
    almacen=fields.Many2one(
        'llantas_config.almacen',
        string="Almacen",
        tracking=True
    )
    
    fecha_proveedor=fields.Date(
        string="Fecha validez",
        tracking=True
    )
    
    codigo_producto=fields.Many2one(
        "product.supplierinfo",
        string="Producto",
        tracking=True
    )
  
    proveedor_id=fields.Char(
        related="codigo_producto.partner_id.name",
        string="Proveedor",
        tracking=True
        
    )
    
    producto=fields.Char(
        related="codigo_producto.product_name",
        string="Nombre producto"
    )

    existencia=fields.Integer(
        string="Existencias",
        tracking=True
    )
    
    costo_sin_iva=fields.Float(
        string="Costo",
        tracking=True
    )

    tipo_cambio=fields.Float(
        string="Tipo de cambio"
    )

    moneda=fields.Many2one(
        "res.currency",
        string="Moneda",
    )

    sku=fields.Char(
        string="Sku",
    )


    
class ProductSupplierinfoInherited(models.Model):
    _inherit = 'product.supplierinfo'
    
    def name_get(self):
        res = super(ProductSupplierinfoInherited, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.partner_id.name)
            display_value += ' - $'
            display_value += str(e.price) or ""
            display_value += ' ['
            display_value += str(e.currency_id.name) or ""
            display_value += ']'
            data.append((e.id, display_value))
        return data

class ctrl_llantas(models.Model): 
    _name = "llantas_config.ctt_prov_cargar"
    _description = "Cargar Existencia"
    
    cargar_nombre_proveedor=fields.Char(
        string="Nombre proveedor",
        tracking=True
        
    )

    cargar_almacen=fields.Char(
        string="Almacen",
        tracking=True
    )
    
    
    fecha_proveedor=fields.Date(
        string="Fecha validez",
        tracking=True
    )
    

    cargar_codigo_producto=fields.Char(
        string="Producto",
        tracking=True
    )
    

    cargar_producto=fields.Char(
        string="Nombre producto"
    )
    
    
    existencia=fields.Integer(
        string="Existencias",
        tracking=True
    )
    
    costo_sin_iva=fields.Float(
        string="Costo",
        tracking=True
    )

    tipo_cambio=fields.Float(
        string="Tipo de cambio"
    )

    moneda=fields.Many2one(
        "res.currency",
        string="Moneda",
    )


class ctrl_tiredirect(models.Model): 
    _name = "llantas_config.ctt_tiredirect_cargar"
    _description = "Cargar Existencia"

    clave_parte=fields.Char(
        string="Clave Parte",
        tracking=True,
    )
    
    
    description_description=fields.Char(
        string="Descripción",
        tracking=True,
    )
    

    moneda_currency=fields.Char(
        string="Moneda",
        tracking=True,
    )
    

    TC=fields.Float(
        string="Tipo de Cambio",
        tracking=True,
    )
    
    
    ES=fields.Float(
        string="ES",
        tracking=True,
    )
    
    FS=fields.Float(
        string="FS",
        tracking=True,
    )
    
    Existencia_Stock=fields.Integer(
        string="Existencias",
        tracking=True,
    )
