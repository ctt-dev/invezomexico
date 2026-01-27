# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError , UserError
import logging

_logger = logging.getLogger(__name__)


class account_move(models.Model):
    _inherit = 'account.move'
    _description = 'Asientos contables'

    def _l10n_mx_edi_add_payment_cfdi_values(self, cfdi_values, pay_results):
        self.ensure_one()

        if self.journal_id.l10n_mx_address_issued_id:
            cfdi_values['issued_address'] = self.journal_id.l10n_mx_address_issued_id

        super()._l10n_mx_edi_add_payment_cfdi_values(cfdi_values, pay_results)

    
    
    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        string="Documento relacionado"
    )
    
    def asignar_cfdi(self):
        context = {
            'default_move_id': self.id,
            'default_date': self.invoice_date,
            'default_partner_id_vat': self.partner_id.vat,
            'default_move_id_type': self.move_type
        }
            
        return {
            'name': 'Relacionar Documento',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_mx_cfdi_manager.wz_account_move_related_doc').id,
            'res_model': 'l10n_mx.cfdi_document_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
    
    def unlink_cfdi(self):
        for rec in self:
            rec.cfdi_document.write({
                'link_state':'unlink'
            })
            rec.cfdi_document = False

    def action_post(self):
        if self.cfdi_document:
            if self.cfdi_document.total != self.amount_total:
                if round(abs(self.cfdi_document.total - self.amount_total),2) > self.env.company.dif_allowed:
                    raise UserError("La diferencia entre el total del asiento contable y el CFDI relacionado es mayor a $" + "{:.2f}".format(self.env.company.dif_allowed) + " pesos.")
        res = super(account_move, self).action_post()
        return res  
    
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
             'cfdi_document': False,
        })
        
        record = super(account_move, self).copy(default)
        return record

    def action_multi_link_docs(self):
        # _logger.warning(f'Facturas: {len(self)}')
        for invoice in self:
            # _logger.warning(f'Invoice: {invoice.name}')
            cfdi_doc = self.env['l10n_mx.cfdi_document'].search([
                ('link_state', '=', 'unlink'),
                ('type_emision', '=', 'R'),
                ('type_comprobante', '=', 'I'),
                ('company_id', 'in', self.env.company.ids),
                ('date', '=', invoice.invoice_date),
                ('rfc_emisor', '=', invoice.partner_id.vat),
                '&',
                ('total', '>=', abs(invoice.amount_total_in_currency_signed + self.env.company.dif_allowed)),
                ('total', '<=', abs(invoice.amount_total_in_currency_signed - self.env.company.dif_allowed)),
            ])
            # _logger.warning(f'Docs: {len(cfdi_doc)}')

            # raise UserError('')
            if len(cfdi_doc) == 1:
                invoice.write({'cfdi_document':cfdi_doc.id})
                cfdi_doc.write({'link_state':'link'})

            elif len(cfdi_doc) > 1:
                invoice_ref = invoice.ref.split(' ')[0]
                for doc in cfdi_doc:
                    if invoice_ref == doc.folio:
                        invoice.write({'cfdi_document':doc.id})
                        doc.write({'link_state':'link'})