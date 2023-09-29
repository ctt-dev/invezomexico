from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class sale_inherit(models.Model):
    _inherit = 'sale.order'
    _description = 'Modelo de modelo alterno'

    def _prepare_invoice_portal(self, razon_social, rfc, email, zip, forma_pago, cfdi, regimen):
        invoice_vals = self._prepare_invoice()
        if self.marketplace.id:
            if self.marketplace.diarios_id.id:
                invoice_vals.update({'journal_id': self.marketplace.diarios_id.id})
        invoice_vals.update({
            'journal_id': razon_social
        })
        return invoice_vals