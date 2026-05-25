# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError, UserError

class account_move(models.Model):
    _inherit = 'account.move'
    
    cacrm_cancelled_by_reversal = fields.Boolean(
        string="¿Cancelled by reversal?", 
        default=False
    )

    cacrm_tax_cash_basis_origin_move_id = fields.Many2one(
        'account.move',
        string="Cash Basis Origin (Original)"
    )

    cacrm_tax_cash_basis_rec_id = fields.Many2one(
        'account.partial.reconcile',
        string="Tax Cash Basis Entry of (Original)"
    )

    def cancel_reversed_moves(self):
        company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        for company_id in company_ids:
            journal_ids = []
            for cacrm_journal_id in company_id.cacrm_journal_ids:
                if cacrm_journal_id.id not in journal_ids:
                    journal_ids.append(cacrm_journal_id.id)

            tax_lock_date = date(1970, 1, 1) ## Establecer fecha al inicio de la época
            if company_id.tax_lock_date:
                tax_lock_date = company_id.tax_lock_date
            moves = self.env['account.move'].search([('company_id','=',company_id.id),('date','>',tax_lock_date),('reversed_entry_id','!=',False),('state','=','posted'),('move_type','=','entry'),('journal_id','in',journal_ids)])
    
            if moves:
                for rec in moves:
                    if rec.reversed_entry_id.id:
                        if rec.journal_id.type == 'general':
                            if rec.date > tax_lock_date and rec.reversed_entry_id.date > tax_lock_date:
                                full_reconcile_ids = rec.env['account.full.reconcile'].search([('exchange_move_id','in',[rec.id, rec.reversed_entry_id.id])])
                                full_reconcile_ids.write({'exchange_move_id': False})
                                partial_reconcile_ids = rec.env['account.partial.reconcile'].search([('exchange_move_id','in',[rec.id, rec.reversed_entry_id.id])])
                                partial_reconcile_ids.write({'exchange_move_id': False})
                        
                                tax_cash_basis_rec_id = rec.tax_cash_basis_rec_id
                                tax_cash_basis_origin_move_id = rec.tax_cash_basis_origin_move_id
                                rec.write({'tax_cash_basis_rec_id': False, 'tax_cash_basis_origin_move_id':False})
                                rec.button_draft()
                                rec.button_cancel()
                                rec.write({'cacrm_cancelled_by_reversal': True, 'cacrm_tax_cash_basis_rec_id': tax_cash_basis_rec_id, 'cacrm_tax_cash_basis_origin_move_id':tax_cash_basis_origin_move_id})
                        
                                tax_cash_basis_rec_id = rec.reversed_entry_id.tax_cash_basis_rec_id
                                tax_cash_basis_origin_move_id = rec.reversed_entry_id.tax_cash_basis_origin_move_id
                                rec.reversed_entry_id.write({'tax_cash_basis_rec_id': False, 'tax_cash_basis_origin_move_id':False})
                                rec.reversed_entry_id.button_draft()
                                rec.reversed_entry_id.button_cancel()
                                rec.reversed_entry_id.write({'cacrm_cancelled_by_reversal': True, 'cacrm_tax_cash_basis_rec_id': tax_cash_basis_rec_id, 'cacrm_tax_cash_basis_origin_move_id':tax_cash_basis_origin_move_id})