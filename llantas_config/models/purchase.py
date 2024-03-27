from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

    
class purchase_order_line_inherit(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'lineas orden de compra'

    

    codigo_proveedor=fields.Char(
        string="Codigo proveedor",
        tracking=True
    )

    product_category = fields.Many2one(
        "product.category",
        string="Categoría de producto",
        related="product_id.categ_id",
        store=True,
    )

    proveedor = fields.Many2one(
        "res.partner",
        string="Proveedor",
        related="partner_id",
        store=True,
    )

    pronto_pago = fields.Many2one(
        "llantas_config.pronto_pago",
        string="Pronto pago",
        store=True,
        domain="[('product_category','=', product_category), ('partner_id','=', proveedor)]"
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_category = self.product_id.categ_id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.proveedor = self.partner_id

    @api.depends('pronto_pago', 'pronto_pago.pronto_pago_porcentaje', 'product_qty', 'price_unit', 'taxes_id')
    def _total_pronto_pago_compute(self):
        for rec in self:
            total_orden = (rec.product_qty * rec.price_unit) * (1 + (rec.taxes_id.amount / 100))
            rec.descuento = total_orden * (rec.pronto_pago.pronto_pago_porcentaje / 100)
            total_con_descuento = total_orden - rec.descuento
            rec.total_pronto_pago = total_con_descuento
    total_pronto_pago=fields.Float(
        string="Total pronto pago",
        compute='_total_pronto_pago_compute',
    )
    descuento=fields.Float(
        string="Descuento",
        compute='_total_pronto_pago_compute',
    )
    
    
class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'
    _description = 'Orden de compra'
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        
        # Inicializamos variables para almacenar la suma de días de vencimiento y el porcentaje de pronto pago
        total_dias_vencimiento = 0
        total_porcentaje_pronto_pago = 0
        total_descuento = 0
        
        # Iteramos sobre las líneas de pedido para calcular la suma de días de vencimiento y el porcentaje de pronto pago
        for line in self.order_line:
            if line.pronto_pago:
                total_descuento += line.descuento

        # Guardamos los resultados en las variables correspondientes de invoice_vals
        invoice_vals['pronto_pago_dias_vencimiento'] = line.pronto_pago.pronto_pago_dias_vencimiento
        invoice_vals['pronto_pago_porcentaje'] = line.pronto_pago.pronto_pago_porcentaje
        invoice_vals['pronto_pago_descuento'] = total_descuento
        
        return invoice_vals


    # @api.onchange('partner_id')
    # def update_pronto_pago_data(self):
    #     self.pronto_pago_dias_vencimiento = self.partner_id.pronto_pago_dias_vencimiento
    #     self.pronto_pago_porcentaje = self.partner_id.pronto_pago_porcentaje

    # pronto_pago_dias_vencimiento = fields.Integer(
    #     string="Pronto pago - Días para vencimiento"
    # )

    # pronto_pago_porcentaje = fields.Float(
    #     string="Pronto pago - Porcentaje de descuento"
    # )
    
    # @api.constrains('pronto_pago_dias_vencimiento')
    # def _check_pronto_pago_dias_vencimiento(self):
    #     for rec in self:
    #         if rec.pronto_pago_dias_vencimiento < 0:
    #             raise ValidationError("No puede seleccionar una cantidad negativa para los días de vencimiento de pronto pago. Corrija para continuar...")
    
    # @api.constrains('pronto_pago_porcentaje')
    # def _check_pronto_pago_porcentaje(self):
    #     for rec in self:
    #         if rec.pronto_pago_porcentaje < 0 or rec.pronto_pago_porcentaje > 100:
    #             raise ValidationError("Solo puede registrar un descuento de entre el 0% y 100% para pronto pago. Corrija para continuar...")


    # pronto_pago=fields.Many2one(
    #     "llantas_config.pronto_pago",
    #     string="Pronto pago",
    #     store=True,
    #     domain="[('partner_id','=',partner_id)]"
    # )