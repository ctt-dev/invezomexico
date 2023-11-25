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

class parcelas_(models.Model):
    _name = 'adrone_config.parcelas'
    _description = 'Parcelas'
    _order = 'id desc'
    
    name = fields.Char(
        string="Nombre"
    )
    
    descripcion=fields.Char(
        string="Descripción",
    )

class cultivos_(models.Model):
    _name = 'adrone_config.cultivos'
    _description = 'Cultivos'
    _order = 'id desc'
    
    name = fields.Char(
        string="Nombre"
    )
    
    descripcion=fields.Char(
        string="Descripción",
    )