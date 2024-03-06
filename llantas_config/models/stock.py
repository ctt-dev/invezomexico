from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_order_inherit(models.Model):
    _inherit = 'stock.picking'
    _description='stock_picking'

    carrier=fields.Char(
        string="Carrier",
        related="sale_id.llantas_config_carrier_id.name",
        readonly=True,
    )

    no_venta=fields.Char(
        related="sale_id.folio_venta",
        string="No. Venta",
        tracking=True,
    )

    no_recoleccion=fields.Char(
        string="No. Recoleccion",
        tracking=True,
        
    )

    link_guia=fields.Char(
        string="Link guia",
        related="sale_id.link_guia",
        readonly=True,
    )

    tdp=fields.Char(
        string="Referencia de compra (TDP)",
        related="purchase_id.partner_ref",
    )

    fecha_entrega=fields.Date(
        string="Fecha entrega",
        tracking=True
    )

    carrier_tracking_ref=fields.Char(
        string="Guia de rastreo",
        related="sale_id.guia",
        readonly=True,
    )

    # carrier_id=fields.Many2one(
    #     "llantas_config.carrier",
    #     string="Carrier",
    # )

    

    # def _compute_rastreador(self):
    #     for rec in self:
    #         carriers = self.env['llantas_config.carrier'].search([('is_trackeable', '=', True)])
    #         link = ''
    #         if carriers:
    #             for carrier in carriers:
    #                 if carrier.name == 'DHL':
    #                     link = 'https://www.dhl.com/mx-es/home/rastreo.html?tracking-id=' + str(rec.carrier_tracking_ref) + '&submit=1'
    #                 elif carrier.name == 'FEDEX':
    #                     link = 'https://www.fedex.com/wtrk/track/?action=track&trackingnumber=' + str(rec.carrier_tracking_ref) + '&cntry_code=mx&locale=es_mx'
    #                 else:
    #                     link = str(carrier.url) + str(rec.carrier_tracking_ref)

    #             rec.rastreador = link
    # rastreador = fields.Char(
    #     string="Guía", 
    #     compute="_compute_rastreador", 
    #     readonly=True
    # )
    