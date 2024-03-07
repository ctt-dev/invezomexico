from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_account_journal_inherit(models.Model):
    _inherit = 'account.journal'
    _description = 'Account journal'

    def name_get(self):
        res = super(sale_account_journal_inherit, self).name_get()
        data = []
        for e in self:
            display_value = ''
            display_value += str(e.name)
            display_value += ' ('
            display_value += str(e.company_id.name) or ""
            display_value += ')'
            data.append((e.id, display_value))
        return data