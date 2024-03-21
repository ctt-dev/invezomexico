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


class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'
    _description = 'Orden de compra'
    
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals['pronto_pago_dias_vencimiento'] = self.pronto_pago_dias_vencimiento
        invoice_vals['pronto_pago_porcentaje'] = self.pronto_pago_porcentaje
        return invoice_vals

    @api.onchange('partner_id')
    def update_pronto_pago_data(self):
        self.pronto_pago_dias_vencimiento = self.partner_id.pronto_pago_dias_vencimiento
        self.pronto_pago_porcentaje = self.partner_id.pronto_pago_porcentaje

    pronto_pago_dias_vencimiento = fields.Integer(
        string="Pronto pago - Días para vencimiento"
    )

    pronto_pago_porcentaje = fields.Float(
        string="Pronto pago - Porcentaje de descuento"
    )
    
    @api.constrains('pronto_pago_dias_vencimiento')
    def _check_pronto_pago_dias_vencimiento(self):
        for rec in self:
            if rec.pronto_pago_dias_vencimiento < 0:
                raise ValidationError("No puede seleccionar una cantidad negativa para los días de vencimiento de pronto pago. Corrija para continuar...")
    
    @api.constrains('pronto_pago_porcentaje')
    def _check_pronto_pago_porcentaje(self):
        for rec in self:
            if rec.pronto_pago_porcentaje < 0 or rec.pronto_pago_porcentaje > 100:
                raise ValidationError("Solo puede registrar un descuento de entre el 0% y 100% para pronto pago. Corrija para continuar...")