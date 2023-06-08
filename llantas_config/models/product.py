from odoo import models, fields, api, _
import logging
import datetime
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class product_template_inherit(models.Model):
    _inherit = 'product.template'
    _description='Producto'

    codigo_llanta = fields.Char(
    string='Codigo',
    )

    marca_llanta = fields.Many2one('country_config.actividad_eco', string="Actividad Economica")