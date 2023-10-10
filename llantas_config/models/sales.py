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
        tracking=True,
        company_dependent=True,
    )
    
    comision=fields.Float(
        string="Comisión",
        tracking=True,
    )
    envio=fields.Float(
        string="Envio",
        tracking=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
        company_dependent=True,
        store=True,
    )

    _sql_constraints = [
        ('folio_venta', 'unique(folio_venta)', "Ya existe una venta con este folio. El folio de la venta debe ser único."),
    ]
    
    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
        store=True,
    )
    

    link_venta=fields.Char(
        string="Link de venta",
        tracking=True,
        store=True,
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
        ('09','Devolución'),], 
        string="Estado de la venta", 
        default='01', 
        tracking=True, 
        store=True)

    lineas_orden = fields.Many2one(
        "sale.order.line",
        string="lineas",
    )

    fecha_venta=fields.Datetime(
        string="Fecha venta",
        default=fields.Datetime.now,
        tracking=True,
        store=True
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

    # def _prepare_invoice(self):
    #     inv = super(sale_order_inherit, self)._prepare_invoice()
    #     if self.marketplace.id:
    #         if self.marketplace.diarios_id.id:
    #             if self.marketplace.diarios_id not in self.journal_id:
    #                 self.journal_id = self.marketplace.diarios_id
    #     return inv
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.marketplace.id:
            if self.marketplace.diarios_id.id:
                invoice_vals.update({'journal_id': self.marketplace.diarios_id.id})
            return invoice_vals

class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
    _description='Lineas de la orden de venta'

    proveedor_id=fields.Many2one(
        "product.supplierinfo",
        # related="product_id.product_tmpl_id.partner_id",
        store=True,
        tracking=True,
    )
    

    costo_proveedor=fields.Float(
        related="proveedor_id.price",
        string="Costo",
        tracking=True,
    )

    importe_descuento=fields.Float(
        string="Importe descuento",
    )

    def compute_precio_antes_dec(self):
        for rec in self:
            rec.precio_antes_dec = rec.price_unit + rec.importe_descuento
    precio_antes_dec=fields.Float(
        string="Precio antes descuento",
        compute=compute_precio_antes_dec,
    )

    

    

    