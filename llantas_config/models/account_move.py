from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class account_move_line_inherit(models.Model):
    _inherit = 'account.move.line'
    _description='Account move line'

    no_pedimento=fields.Char(
        string="No. Pedimento",
        tracking=True,
    )

class account_move_inherit(models.Model):
    _inherit = 'account.move'
    _description='Account move line'
    
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

    @api.depends('pronto_pago_porcentaje','amount_total')
    def compute_pronto_pago_descuento(self):
        for rec in self:
            rec.pronto_pago_descuento = rec.amount_total * (rec.pronto_pago_porcentaje / 100)
    pronto_pago_descuento = fields.Float(
        string="Pronto pago - Descuento",
        compute=compute_pronto_pago_descuento,
        store=True
    )

    @api.depends('pronto_pago_descuento','amount_total')
    def compute_pronto_pago_total_con_descuento(self):
        for rec in self:
            rec.pronto_pago_total_con_descuento = rec.amount_total - rec.pronto_pago_descuento
    pronto_pago_total_con_descuento = fields.Float(
        string="Pronto pago - Total con descuento",
        compute=compute_pronto_pago_total_con_descuento,
        store=True
    )