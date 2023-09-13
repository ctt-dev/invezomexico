from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'
    _description='Orden de venta'

    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        required=True,
        tracking=True,
    )

    comision=fields.Monetary(
        string="Comisión",
        tracking=True,
    )
    envio=fields.Monetary(
        string="Envio",
        tracking=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
    )

    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
    )

    link_venta=fields.Char(
        string="Link de venta",
        tracking=True
    )

    status_ventas=fields.Many2one(
        "llantas_config.status_ventas",
        string="Estatus",
        tracking=True,
    )

    status_venta=fields.One2many(
        "llantas_config.status_ventas",
        "name",
        string="Estatus",
        tracking=True,
    )

    ventas_status = fields.Selection([
        ('01','Pendiente'),
        ('02','Debito en curso'),
        ('03','Traspaso'),
        ('04','Guia pendiente'),
        ('05','Enviado'),
        ('06','Entregado'),
        ('07','Cerrado'),
        ('08','Incidencia'),
        ('09','Devolución'),
    ], string="Estado de la venta", default='01', tracking=True, store=True)

    lineas_orden = fields.Many2one(
        "sale.order.line",
        string="lineas",
    )

    fecha_venta=fields.Datetime(
        string="Fecha venta",
        default=fields.Datetime.now,
        tracking=True,
    )

    mostrar_comision=fields.Boolean(
        related="marketplace.mostrar_comision",
    )

    mostrar_envio=fields.Boolean(
        related="marketplace.mostrar_envio",
    )

    def action_confirm(self):
        res = super(sale_order_inherit, self).action_confirm()
        if self.marketplace.id:
            if self.marketplace.category_id.id:
                if self.marketplace.category_id not in self.partner_id.category_id:
                    self.partner_id.category_id += self.marketplace.category_id
        return res

        

class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
    _description='Lineas de la orden de venta'

    proveedor_id=fields.Many2one(
        "product.supplierinfo",
        store=True,
        tracking=True,
    )

    costo_proveedor=fields.Float(
        related="proveedor_id.price",
        string="Costo",
        tracking=True,
    )

   

    

    

    