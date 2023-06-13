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

    marca_llanta = fields.Many2one(
        'llantas_config.marca_llanta', 
        string="Marca llanta"
    )
    
    modelo_llanta = fields.Many2one(
        'llantas_config.modelo_llanta', 
        string="Modelo llanta"
    )
    
    medida_llanta = fields.Many2one(
        'llantas_config.medida_llanta', 
        string="Medida llanta"
    )

    indice_carga = fields.Integer(
    string='Indice de carga',
    )

    indice_velocidad = fields.Char(
    string='Indice de velocidad',
    )

    largo = fields.Float(
    string='Largo llanta',
    )
    
    ancho = fields.Float(
    string='Ancho llanta',
    )	
    
    alto = fields.Float(
    string='Alto llanta',
    )	

