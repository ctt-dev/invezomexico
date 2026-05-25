# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError

class res_company(models.Model):
    _inherit = 'res.company'
    
    cacrm_journal_ids = fields.Many2many(
        'account.journal',
        string="Journals for automatic reversal"
    )