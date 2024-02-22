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
        related="sale_id.carrier_id.name",
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

    