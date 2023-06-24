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
    
class ProductSupplierinfoInherited(models.Model):
    _inherit = 'product.supplierinfo'
    
    def name_get(self):
        res = super(ProductSupplierinfoInherited, self).name_get()
        data = []
        for e in self:
            display_value = '['
            display_value += str(e.product_code) or ""
            display_value += '] '
            display_value += str(e.product_name) or ""
            display_value += ' - '
            display_value += str(e.partner_id.name) or ""
            data.append((e.id, display_value))
        return data
    