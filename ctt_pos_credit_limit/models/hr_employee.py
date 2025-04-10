from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime

class HrEmployeeCreditLimit(models.Model):
    _inherit = ['hr.employee']

    allow_credit_sale = fields.Boolean('Puede autorizar ventas de crédito',readonly=False, related='user_id.allow_credit_sale', tracking=True)
    allow_aplazo = fields.Boolean('Puede autorizar convenio de venta', readonly=False, related='user_id.allow_aplazo', tracking=True)
    allow_credit_block = fields.Boolean('Puede bloquear crédito de clientes', readonly=False, related='user_id.allow_credit_block', tracking=True)