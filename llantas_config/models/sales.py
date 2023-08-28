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
        required=True,
        tracking=True,
    )

    comision=fields.Monetary(
        string="Comisión",
        tracking=True,
    )
    envio=fields.Monetary(
        string="Envio",
        tracking=True,
    )

    comprador_id=fields.Many2one(
        "hr.employee",
        string="Comprador",
        tracking=True,
    )

    folio_venta=fields.Char(
        string="No. Venta",
        tracking=True,
    )

class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
    _description='Lineas de la orden de venta'

    proveedor_id=fields.Many2one(
        "product.supplierinfo",
        store=True,
        tracking=True,
    )