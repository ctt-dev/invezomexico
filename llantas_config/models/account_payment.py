from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from num2words import num2words
_logger = logging.getLogger(__name__)
import datetime

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    to_check=fields.Boolean(
        string="Por Revisar",
        default=False,
        tracking=True
    )
