from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
import datetime

class account_move_line_inherit(models.Model):
    _inherit = 'account.move.line'
    _description='Account move line'

    # no_pedimento=fields.Char(
    #     string="No. Pedimento",
    #     tracking=True,
    # )

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

    pronto_pago_dias_vencimiento = fields.Integer(
        string="Pronto pago - Días para vencimiento",
        related="pronto_pago.pronto_pago_dias_vencimiento"
    )

    pronto_pago_porcentaje = fields.Float(
        string="Pronto pago - Porcentaje de descuento",
        related="pronto_pago.pronto_pago_porcentaje"
    )

    @api.onchange('dias_transcurridos')
    def onchange_dias_transcurridos(self): 
        # raise UserError("onchange_dias_transcurridos")
        for rec in self:
            pronto_pago_id = False
            pronto_pago_ids = rec.env['llantas_config.pronto_pago'].search([('product_category','=', rec.product_category.id),('partner_id','=', rec.proveedor.id),('pronto_pago_dias_vencimiento','>=', rec.dias_transcurridos)],limit=1)
            if len(pronto_pago_ids) > 0:
                pronto_pago_id = pronto_pago_ids[0]
            rec.pronto_pago = pronto_pago_id
            
    dias_transcurridos = fields.Integer(string="Días transcurridos", compute='_compute_dias_transcurridos', store=True)
    
    # @api.onchange('dias_transcurridos')
    pronto_pago = fields.Many2one(
        "llantas_config.pronto_pago",
        string="Pronto pago",
        domain="[('product_category','=', product_category), ('partner_id','=', proveedor), ('pronto_pago_dias_vencimiento','>=', dias_transcurridos)]",
    )

    @api.depends('invoice_date')
    def _compute_dias_transcurridos(self):
        today_datetime = datetime.datetime.today()
        for factura in self:
            if factura.invoice_date:
                invoice_datetime = datetime.datetime.combine(factura.invoice_date, datetime.datetime.min.time())
                days_diff = (today_datetime - invoice_datetime).days
                factura.dias_transcurridos = days_diff
            else:
                factura.dias_transcurridos = 0


class account_move_inherit(models.Model):
    _inherit = 'account.move'
    _description='Account move line'

    @api.onchange('invoice_date')
    def onchange_invoice_date_update_pronto_pago(self):
        for rec in self:
            for line in rec.line_ids:
                line.onchange_dias_transcurridos()
    
    @api.onchange('partner_id')
    def update_pronto_pago_data(self):
        self.pronto_pago_dias_vencimiento = self.partner_id.pronto_pago_dias_vencimiento
        self.pronto_pago_porcentaje = self.partner_id.pronto_pago_porcentaje

    pronto_pago_dias_vencimiento = fields.Integer(
        string="Pronto pago - Días para vencimiento",
        related="line_ids.pronto_pago_dias_vencimiento"
    )

    pronto_pago_porcentaje = fields.Float(
        string="Pronto pago - Porcentaje de descuento",
        related="line_ids.pronto_pago_porcentaje"
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

    @api.depends('invoice_date','pronto_pago_dias_vencimiento')
    def compute_pronto_pago_fecha_vencimiento(self):
        for rec in self:
            if rec.invoice_date:
                rec.pronto_pago_fecha_vencimiento = rec.invoice_date + datetime.timedelta(days=rec.pronto_pago_dias_vencimiento)
            else:
                rec.pronto_pago_fecha_vencimiento = False
    pronto_pago_fecha_vencimiento = fields.Date(
        string="Pronto pago - Fecha de vencimiento",
        compute=compute_pronto_pago_fecha_vencimiento,
        store=True
    )

    @api.depends('pronto_pago_fecha_vencimiento')
    def compute_pronto_pago_dias_para_vencimiento(self):
        for rec in self:
            if rec.pronto_pago_fecha_vencimiento:
                # raise UserError(int(rec.pronto_pago_fecha_vencimiento - datetime.date.today()))
                rec.pronto_pago_dias_para_vencimiento = int((rec.pronto_pago_fecha_vencimiento - datetime.date.today()).days)
            else:
                rec.pronto_pago_dias_para_vencimiento = 0
            # rec.pronto_pago_dias_para_vencimiento = 0
    pronto_pago_dias_para_vencimiento = fields.Integer(
        string="Pronto pago - Días para vencimiento",
        compute=compute_pronto_pago_dias_para_vencimiento,
        store=False
    )

    @api.depends('pronto_pago_porcentaje', 'amount_total')
    def _total_pronto_pago_compute(self):
        for rec in self:
            rec.pronto_pago_descuento = rec.amount_total * (rec.pronto_pago_porcentaje / 100)    

    pronto_pago_descuento = fields.Float(
        string="Pronto pago - Descuento",
        compute='_total_pronto_pago_compute',
    )

    @api.depends('pronto_pago_descuento','amount_total')
    def compute_pronto_pago_total_con_descuento(self):
        for rec in self:
            rec.pronto_pago_total_con_descuento = rec.amount_total - rec.pronto_pago_descuento
    pronto_pago_total_con_descuento = fields.Float(
        string="Pronto pago - Total con descuento",
        compute=compute_pronto_pago_total_con_descuento,
    )

    @api.depends('amount_total')
    def compute_total_facturado(self):
        for rec in self:
            rec.total_facturado = rec.amount_total
    total_facturado = fields.Float(
        string="Pronto pago - Total con descuento",
        compute=compute_total_facturado,
    )

    marketplace_sale_order=fields.Char(
        string="No. venta",
        related="invoice_line_ids.sale_line_ids.folio_venta"
    )
    
