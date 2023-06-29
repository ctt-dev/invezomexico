from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'
    _description='Producto'

    marketplace = fields.Many2one(
        "llantas_config.marketplaces",
        string="Marketplace",
    )