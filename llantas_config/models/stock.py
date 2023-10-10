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

    carrier=fields.Many2one(
        "llantas_config.carrier",
        string="Carrier",
        tracking=True
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

    tdp=fields.Char(
        string="Referencia de compra (TDP)",
        related="purchase_id.partner_ref",
    )

    fecha_entrega=fields.Date(
        string="Fecha entrega",
        tracking=True
    )

    