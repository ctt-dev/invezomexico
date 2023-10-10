from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  

class contactos(models.Model):
    _inherit = 'res.partner'
    _description = 'Contactos'

    usuario_marketplace=fields.Char(
        string="Usuario marketplace",
    )