from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime

class PosPaymentMethodCreditLimit(models.Model):
    _inherit = 'pos.payment.method'
    
    is_credit = fields.Boolean(string="Es credito")