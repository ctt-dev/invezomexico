
from odoo import fields, models


class AccountJournalCreditLimit(models.Model):
    """Adding POS Credit boolean field in Journals"""
    _inherit = 'account.journal'

    pos_credit = fields.Boolean(string='Credit')
