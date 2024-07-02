# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import pytz
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)



class account_move_line(models.Model):
    _inherit = 'account.move.line'
    
    def name_get(self):
        res = super(account_move_line, self).name_get()
        data = []
        for e in self:
            display_value = '['
            display_value += str(e.move_id.name) or ""
            display_value += '] '
            display_value += ' ' if e.name != False else ""
            display_value += str(e.name) if e.name != False else ""
            display_value += ' - (' if e.partner_id.name != False else ""
            display_value += str(e.partner_id.name) if e.partner_id.name != False else ""
            display_value += ')' if e.partner_id.name != False else ""
            data.append((e.id, display_value))
        return data
    
    ctt_partial_reconcile_line_to_reconcile = fields.Many2one(
        'account.move.line',
        string="Apunte contable a conciliar"
    )
    
    ctt_partial_reconcile_amount_residual_backup = fields.Float(
        string="Importe residual para conciliaciones parciales"
    )