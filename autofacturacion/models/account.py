from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from itertools import groupby
from odoo.fields import Command
_logger = logging.getLogger(__name__)
import datetime
import time
import threading


from collections import defaultdict
from lxml import etree
from lxml.objectify import fromstring
from math import copysign
from datetime import datetime
from zeep import Client
from zeep.transports import Transport
from json.decoder import JSONDecodeError

class account_inherit(models.Model):
    _inherit = 'account.move'
    _description = 'Modelo de modelo alterno'

    @api.onchange('invoice_line_ids')
    def update_lines(self):
        _logger.warning("INVOICELINE")
        for line in self.invoice_line_ids:
            line.name = line.product_id.name

    def action_process_edi_web_services_for_autofacturacion(self, invoice_id):
        invoice_id = self.env['account.move'].browse(invoice_id)
        # raise UserError(invoice_id)
        if invoice_id.state == "posted" and invoice_id.edi_state != "sent":
            invoice_id.action_process_edi_web_services()
            if(invoice_id.edi_error_count == 1):
                invoice_id.action_retry_edi_documents_error()
            # raise UserError(invoice_id)

    # @api.model
    # def action_post(self):
    #     _logger.warning("post")
    #     res = super(account_inherit, self).action_post()
    #     return self.action_invoice_print()

class account_line_inherit(models.Model):
    _inherit = 'account.move.line'
    _description = 'Modelo de modelo alterno'

    @api.model
    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if line.display_type == 'payment_term':
                if line.move_id.payment_reference:
                    _logger.warning("if1")
                    line.name = line.move_id.payment_reference
                elif not line.name:
                    _logger.warning("if2")
                    _logger.warning(line.product_id)
                    line.name = line.product_id.name
                continue
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                _logger.warning("if3")
                continue
            if line.partner_id.lang:
                _logger.warning("if4")
                product = line.product_id.with_context(lang=line.partner_id.lang)
            else:
                _logger.warning("if5")
                product = line.product_id.name

            values = []
            if product.partner_ref:
                values.append(product.partner_ref)
            if line.journal_id.type == 'sale':
                if product.description_sale:
                    values.append(product.description_sale)
            elif line.journal_id.type == 'purchase':
                if product.description_purchase:
                    values.append(product.description_purchase)
            line.name = '\n'.join(values)
    