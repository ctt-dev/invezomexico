from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  

class contactos(models.Model):
    _inherit = 'res.partner'
    _description = 'Contactos'

    usuario_marketplace=fields.Char(
        string="Usuario marketplace",
    )

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