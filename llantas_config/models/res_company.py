from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class res_company_inherit(models.Model):
    _inherit = 'res.company'
    _description='res_company'

    formato_invezo=fields.Boolean(
        string="Formato Invezo",
        tracking=True,
        default=False
    )