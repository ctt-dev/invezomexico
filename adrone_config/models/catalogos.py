from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class tipo_productos(models.Model):
    _name = 'adrone_config.tipo_productos'
    _description = 'Tipos de productos'
    _order = 'id desc'
    
    name = fields.Char(
        string="Nombre"
    )
    
    color = fields.Integer(
        string="Color"
    )