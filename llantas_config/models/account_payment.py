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

    def action_massive_stamp_payment_complements(self):

        for payment in self:
            try:
                invoices = payment.reconciled_invoice_ids.filtered(
                    lambda inv: inv.l10n_mx_edi_update_payments_needed
                )

                if not invoices:
                    continue

                invoices.l10n_mx_edi_cfdi_invoice_try_update_payments()

                _logger.info(
                    "Complemento procesado para pago %s",
                    payment.display_name
                )

            except Exception:
                _logger.exception(
                    "Error al procesar complemento para pago %s",
                    payment.display_name
                )
