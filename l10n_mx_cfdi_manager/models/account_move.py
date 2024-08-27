# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError , UserError


class account_move(models.Model):
    _inherit = 'account.move'
    _description = 'Herencia para relacion cfdi - facturas'
    
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