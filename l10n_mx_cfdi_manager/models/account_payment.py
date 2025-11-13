# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import ValidationError , UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        string="Documento relacionado"
    )

    def asignar_cfdi(self):
        context = {
            'default_payment_id': self.id,
            'default_date': self.date,
            'default_partner_id_vat': self.partner_id.vat,
            'default_move_id_type': 'payment'
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