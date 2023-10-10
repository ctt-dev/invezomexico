from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime
from datetime import timedelta
from datetime import datetime
import urllib.request
import json
# import timedelta

class marketplace_pagos(models.Model):
    _name = 'llantas_config.pagos_marketplace'
    _description = 'Pagos marketplace'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def name_get(self):
        res = super(marketplace_pagos, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.marketplace.name)
            display_value += ' ( '
            display_value += str(e.name) or ""
            display_value += ' )'
            data.append((e.id, display_value))
        return data
    
    sale_id=fields.Many2one(
        "sale.order",
        string="Folio interno",
    )
    
    name = fields.Char(
        string="Folio entrega",
    )
    
    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
        related="sale_id.marketplace",
        # company_dependent=True,
    )

    total_comision=fields.Float(
        string="Comisión",
        related="sale_id.comision",
        store=True
    )
    
    total_envio=fields.Float(
        string="Envio",
        related="sale_id.envio",
        store=True
    )

    total_venta = fields.Float(
        string="Total Venta",
        compute="_compute_total_venta",
    )
    @api.depends('sale_id.amount_total')
    def _compute_total_venta(self):
        for record in self:
            record.total_venta = record.sale_id.amount_total
    
    folio_venta=fields.Char(
        string="No. Venta",
        related="sale_id.folio_venta",
    )
    
    link_venta=fields.Char(
        string="Link de venta",
        related="sale_id.link_venta",
    )

    fecha_venta=fields.Datetime(
        string="Fecha venta",
        related="sale_id.fecha_venta",
    )

    envio_id=fields.Many2one(
        "stock.picking",
        string="Salida",
    )

    company_id=fields.Many2one(
        "res.company",
        string="Empresa",
    )

    

    status_pago=fields.Selection(
        [
            ('01', 'Pendiente'),
            ('02', 'Pagado'),
            ('03', 'Cancelado'),
        ],
        string="Estatus pago",default="01",
    )

    @api.model
    def create(self, values):
        values['company_id'] = self.env.company.id
        return super(marketplace_pagos, self).create(values)

    total_a_pagar=fields.Float(
        string="Total a pagar",
        compute="_total_a_pagar_compute",
    )
    @api.depends('total_envio','total_comision','total_venta')
    def _total_a_pagar_compute(self):
        for rec in self:
            if rec.marketplace.name == 'COPPEL':
                rec.total_a_pagar = rec.total_venta - (rec.total_envio + rec.total_comision)
            if rec.marketplace.name == 'SEARS' or rec.marketplace.name == 'CLAROSHOP':
                rec.total_a_pagar = rec.total_venta - rec.total_comision

    fecha_entrega=fields.Date(
        string="Fecha entrega",
        related="envio_id.fecha_entrega",
    )
    
    fecha_14 = fields.Date(
        string="Fecha de 14 días",
        compute='_fecha_14_compute'
    )

    def _fecha_14_compute(self):
        for rec in self:
            if rec.marketplace.name == 'COPPEL':
                fecha_14 = rec.fecha_entrega + timedelta(days=14)
                rec.fecha_14 = fecha_14.strftime('%Y-%m-%d')
            if rec.marketplace.name != 'COPPEL':
                rec.fecha_14=''

    def calcular_fecha_pago(self):
        for rec in self:
            if rec.marketplace.name == 'COPPEL':
                fecha_efectiva = rec.fecha_entrega + timedelta(days=14)
                while fecha_efectiva.day not in [1, 8, 16, 24]:
                    fecha_efectiva += timedelta(days=1)

                if fecha_efectiva <= rec.fecha_entrega:
                    fecha_efectiva = fecha_efectiva.replace(month=fecha_efectiva.month + 1, day=1)
                    while fecha_efectiva.day not in [1, 8, 16, 24]:
                        fecha_efectiva += timedelta(days=1)
                rec.fecha_efectiva=fecha_efectiva.strftime('%Y-%m-%d')
            if rec.marketplace.name == 'SEARS' or rec.marketplace.name == 'CLAROSHOP':
                dia_entrega = rec.fecha_entrega.day
                mes_entrega = rec.fecha_entrega.month
                anio_entrega = rec.fecha_entrega.year

                if 1 <= dia_entrega <= 7:
                    fecha_pago = datetime(anio_entrega, mes_entrega, 18)
                elif 8 <= dia_entrega <= 15:
                    fecha_pago = datetime(anio_entrega, mes_entrega, 26)
                elif 16 <= dia_entrega <= 23:
                    if mes_entrega == 12:
                        fecha_pago = datetime(anio_entrega + 1, 1, 4)
                    else:
                        fecha_pago = datetime(anio_entrega, mes_entrega + 1, 4)
                elif 24 <= dia_entrega <= 31:
                    if mes_entrega == 12:
                        fecha_pago = datetime(anio_entrega + 1, 1, 12)
                    else:
                        fecha_pago = datetime(anio_entrega, mes_entrega + 1, 12)
                rec.fecha_efectiva=fecha_pago.strftime('%Y-%m-%d')
                
        
    fecha_efectiva = fields.Date(
        string="Fecha efectiva de pago",
        compute=calcular_fecha_pago
    )

    def cambiar_a_pagado(self):
        for rec in self:
            rec.status_pago = '02'
    def cambiar_a_cancelado(self):
        for rec in self:
            rec.status_pago = '03'
    def cambiar_a_pendiente(self):
        for rec in self:
            rec.status_pago = '01'

    diferencia_dias_pago=fields.Integer(
        string="Diferencia de dias recepcion y pago",
        compute='diferencia_dias_pago_compute'
    )

    def diferencia_dias_pago_compute(self):
        for rec in self:
            diferencia = rec.fecha_efectiva - rec.fecha_entrega
            rec.diferencia_dias_pago=diferencia.days
            
    
    
    