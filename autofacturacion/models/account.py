from odoo import api, fields, models, _, Command
from odoo.addons.base.models.decimal_precision import DecimalPrecision
from odoo.addons.account.tools import format_rf_reference
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from odoo.tools import (
    date_utils,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    float_repr,
    format_amount,
    format_date,
    formatLang,
    frozendict,
    get_lang,
    is_html_empty,
    sql
)
import logging
import json
from itertools import groupby
from odoo.fields import Command
_logger = logging.getLogger(__name__)
import datetime
import time

class sale_inherit(models.Model):
    _inherit = 'account.move'
    _description = 'Modelo de modelo alterno'
    
    def action_post_portal(self):
        ''' draft -> posted '''
        self.move_id._post_portal(soft=False)

        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()
        
class sale_inherit(models.Model):
    _inherit = 'account.move'
    _description = 'Modelo de modelo alterno'

    def action_post_portal(self):
        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post_portal()
        if other_moves:
            other_moves._post_portal(soft=False)
        return self
        
    def _post_portal(self, soft=True):
        """Post/Validate the documents.

        Posting the documents will give it a number, and check that the document is
        complete (some fields might not be required if not posted but are required
        otherwise).
        If the journal is locked with a hash table, it will be impossible to change
        some fields afterwards.

        :param soft (bool): if True, future documents are not immediately posted,
            but are set to be auto posted automatically at the set accounting date.
            Nothing will be performed on those documents before the accounting date.
        :return Model<account.move>: the documents that have been posted
        """
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You don't have the access rights to post an invoice."))

        for invoice in self.filtered(lambda move: move.is_invoice(include_receipts=True)):
            if invoice.quick_edit_mode and invoice.quick_edit_total_amount and invoice.quick_edit_total_amount != invoice.amount_total:
                raise UserError(_(
                    "The current total is %s but the expected total is %s. In order to post the invoice/bill, "
                    "you can adjust its lines or the expected Total (tax inc.).",
                    formatLang(self.env, invoice.amount_total, currency_obj=invoice.currency_id),
                    formatLang(self.env, invoice.quick_edit_total_amount, currency_obj=invoice.currency_id),
                ))
            if invoice.partner_bank_id and not invoice.partner_bank_id.active:
                raise UserError(_(
                    "The recipient bank account linked to this invoice is archived.\n"
                    "So you cannot confirm the invoice."
                ))
            if float_compare(invoice.amount_total, 0.0, precision_rounding=invoice.currency_id.rounding) < 0:
                raise UserError(_(
                    "You cannot validate an invoice with a negative total amount. "
                    "You should create a credit note instead. "
                    "Use the action menu to transform it into a credit note or refund."
                ))

            if not invoice.partner_id:
                if invoice.is_sale_document():
                    raise UserError(_("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif invoice.is_purchase_document():
                    raise UserError(_("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            if not invoice.invoice_date:
                if invoice.is_sale_document(include_receipts=True):
                    invoice.invoice_date = fields.Date.context_today(self)
                elif invoice.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))

        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            for move in future_moves:
                if move.auto_post == 'no':
                    move.auto_post = 'at_date'
                msg = _('This move will be posted at the accounting date: %(date)s', date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        for move in to_post:
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.line_ids.filtered(lambda line: line.display_type not in ('line_section', 'line_note')):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post != 'no' and move.date > fields.Date.context_today(self):
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s", date_msg))
            if not move.journal_id.active:
                raise UserError(_(
                    "You cannot post an entry in an archived journal (%(journal)s)",
                    journal=move.journal_id.display_name,
                ))
            if move.display_inactive_currency_warning:
                raise UserError(_(
                    "You cannot validate a document with an inactive currency: %s",
                    move.currency_id.name
                ))

            if move.line_ids.account_id.filtered(lambda account: account.deprecated):
                raise UserError(_("A line of this move is using a deprecated account, you cannot post it."))

            affects_tax_report = move._affect_tax_report()
            lock_dates = move._get_violated_lock_dates(move.date, affects_tax_report)
            if lock_dates:
                move.date = move._get_accounting_date(move.invoice_date or move.date, affects_tax_report)

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        to_post.line_ids._create_analytic_lines()

        # Trigger copying for recurring invoices
        to_post.filtered(lambda m: m.auto_post not in ('no', 'at_date'))._copy_recurring_entries()

        for invoice in to_post:
            # Fix inconsistencies that may occure if the OCR has been editing the invoice at the same time of a user. We force the
            # partner on the lines to be the same as the one on the move, because that's the only one the user can see/edit.
            wrong_lines = invoice.is_invoice() and invoice.line_ids.filtered(lambda aml:
                aml.partner_id != invoice.commercial_partner_id
                and aml.display_type not in ('line_note', 'line_section')
            )
            if wrong_lines:
                wrong_lines.write({'partner_id': invoice.commercial_partner_id.id})

        to_post.write({
            'state': 'posted',
            'posted_before': True,
        })
        _logger.warning("SALE")
        while (self.state != 'posted'):
            _logger.warning("WAIT")
            time.sleep(3)
        try:
            while True:
                _logger.warning("timbrando")
                _logger.warning(self)
                self.action_process_edi_web_services()
                #moves.action_retry_edi_documents_error()
                # _logger.warning(moves.l10n_mx_edi_payment_method_id)
                # _logger.warning(moves.l10n_mx_edi_payment_policy)
                if(self.edi_error_count == 1):
                    raise ValidationError(_(self.edi_error_message))
                    _logger.warning("error")
                    return
                else:
                    _logger.warning(self.edi_document_ids)
                    return
                    for x in self.edi_document_ids:
                        _logger.warning(x.name)
                        if(x.edi_format_name == 'CFDI (4.0)'):
                            return {
                                'type': 'ir.actions.act_url',
                                'url': '/autofacturador/xml_report/%s' % (x.id),
                                'target': 'self',
                            }
        except ValidationError as exc:
            raise ValidationError(_(exc))
        except UserError as excUser:
            raise UserError(_(excUser))
            
        for invoice in to_post:
            invoice.message_subscribe([
                p.id
                for p in [invoice.partner_id]
                if p not in invoice.sudo().message_partner_ids
            ])

            if (
                invoice.is_sale_document()
                and invoice.journal_id.sale_activity_type_id
                and (invoice.journal_id.sale_activity_user_id or invoice.invoice_user_id).id not in (self.env.ref('base.user_root').id, False)
            ):
                invoice.activity_schedule(
                    date_deadline=min((date for date in invoice.line_ids.mapped('date_maturity') if date), default=invoice.date),
                    activity_type_id=invoice.journal_id.sale_activity_type_id.id,
                    summary=invoice.journal_id.sale_activity_note,
                    user_id=invoice.journal_id.sale_activity_user_id.id or invoice.invoice_user_id.id,
                )

        customer_count, supplier_count = defaultdict(int), defaultdict(int)
        for invoice in to_post:
            if invoice.is_sale_document():
                customer_count[invoice.partner_id] += 1
            elif invoice.is_purchase_document():
                supplier_count[invoice.partner_id] += 1
        for partner, count in customer_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        for partner, count in supplier_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        # Trigger action for paid invoices if amount is zero
        to_post.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        )._invoice_paid_hook()

        

