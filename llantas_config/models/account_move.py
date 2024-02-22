from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class account_move_line_inherit(models.Model):
    _inherit = 'account.move.line'
    _description='Account move line'

    no_pedimento=fields.Char(
        string="No. Pedimento",
        tracking=True,
    )