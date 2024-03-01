from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_order_inherit(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'lineas orden de compra'

    no_pedimento=fields.Char(
        string="# pedimiento",
        trackin=True,
    )

    codigo_proveedor=fields.Char(
        string="Codigo proveedor",
        tracking=True
    )
