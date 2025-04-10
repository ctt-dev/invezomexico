from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime

class ResUsersCreditLimit(models.Model):
    _inherit = 'res.users'

    allow_credit_sale = fields.Boolean('Puede autorizar ventas de crédito')
    allow_aplazo = fields.Boolean('Puede autorizar convenio de venta')
    allow_credit_block = fields.Boolean('Puede bloquear crédito de clientes')
    