# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import pytz
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)



class res_company(models.Model):
    _inherit = 'res.company'
    
    ctt_partial_reconcile_journal_id = fields.Many2one(
        'account.journal',
        string="Diario para asientos de transición"
    )