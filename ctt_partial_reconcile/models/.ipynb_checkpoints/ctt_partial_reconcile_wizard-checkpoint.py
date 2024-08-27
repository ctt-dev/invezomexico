# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import pytz
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)



class ctt_partial_reconcile_wizard(models.TransientModel):
    _name = 'ctt_partial_reconcile.wizard' 
    _description = "Wizard para Conciliaciones parciales"
    
    @api.onchange('type')
    def onchange_type(self):
        self.account_id = False
        self.line_ids = False
        self.line_ids_opc_1 = False
        self.line_ids_opc_2 = False
    
    @api.onchange('account_id')
    def onchange_account_id(self):
        self.line_ids = False
        self.line_ids_opc_1 = False
        self.line_ids_opc_2 = False
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.line_ids = False
        self.line_ids_opc_1 = False
        self.line_ids_opc_2 = False
    
    partner_id = fields.Many2one(
        'res.partner',
        string="Contacto"
    )
    
    type = fields.Selection(
        [
            ('receivable','Por Cobrar'),
            ('payable','Por Pagar'),
        ],
        string="Tipo de cuenta",
        default="receivable",
        required=1
    )
    account_id = fields.Many2one(
        'account.account',
        string="Cuenta contable",
    )
    
    line_ids = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id',
        string="Líneas a conciliar"
    )
    
    line_ids_opc_1 = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id_1',
        string="Líneas a conciliar - Opción 1"
    )
    
    line_ids_opc_2 = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id_2',
        string="Líneas a conciliar - Opción 2"
    )
    
    def reconcile(self):
        if len(self.line_ids_opc_1) > 0:
            self.line_ids = self.line_ids_opc_1
        if len(self.line_ids_opc_2) > 0:
            self.line_ids = self.line_ids_opc_2
            
        if self.env.company.ctt_partial_reconcile_journal_id.id == False:
            raise UserError("Es necesario especificar un Diario para traslados en la compañía. Configure uno para continuar...")
        if len(self.line_ids) < 2:
            raise UserError("Debe incluir por lo menos 2 apuntes contables con un monto total de 0.00 para continuar...")
        check_list = []
        for line in self.line_ids:
            if round(line.amount,2) == 0:
                raise UserError("NO debe incluir líneas con un monto de 0.00. Eliminelas para continuar...")
            if line.line_id.id in check_list:
                raise UserError("NO debe incluir 2 veces el mismo apunte contable para la conciliación...")
            if line.line_id.id not in check_list:
                check_list.append(line.line_id.id)
        total_amount = 0
        for line in self.line_ids:
            total_amount += line.amount
        if round(total_amount,2) != 0:
            raise UserError("El monto total debe ser 0.00 para continuar...")
        
        lines_to_reconcile = self.env['account.move.line']
        move_lines = []
        c = 0
        for line in self.line_ids:
            if line.line_id_debit > 0:
                if round(abs(line.line_id_amount_residual) - abs(line.amount),2) != 0:
                    c += 1
                    move_lines.append((0, 0, {
                        'name': str(c),
                        'debit': 0,
                        'credit': abs(line.line_id_amount_residual) - abs(line.amount),
                        'account_id': self.account_id.id,
                        'partner_id': self.partner_id.id,
                        'ctt_partial_reconcile_line_to_reconcile': line.line_id.id,
                    }))
                    move_lines.append((0, 0, {
                        'name': str(c),
                        'debit': abs(line.line_id_amount_residual) - abs(line.amount),
                        'credit': 0,
                        'account_id': self.account_id.id,
                    }))
            if line.line_id_credit > 0:
                if round(abs(line.line_id_amount_residual) - abs(line.amount),2) != 0:
                    c += 1
                    move_lines.append((0, 0, {
                        'name': str(c),
                        'debit': abs(line.line_id_amount_residual) - abs(line.amount),
                        'credit': 0,
                        'account_id': self.account_id.id,
                        'partner_id': self.partner_id.id,
                        'ctt_partial_reconcile_line_to_reconcile': line.line_id.id,
                    }))
                    move_lines.append((0, 0, {
                        'name': str(c),
                        'debit': 0,
                        'credit': abs(line.line_id_amount_residual) - abs(line.amount),
                        'account_id': self.account_id.id,
                    }))
        if len(move_lines) > 0:
            move = self.env['account.move'].create({
                'journal_id': self.env.company.ctt_partial_reconcile_journal_id.id,
                'currency_id': self.env.company.currency_id.id,
                'move_type': 'entry',
                'date': datetime.date.today(),
                'line_ids': move_lines,
            })
            move.action_post()
            for line in move.line_ids:
                lines_to_reconcile = self.env['account.move.line']
                if line.ctt_partial_reconcile_line_to_reconcile.id != False:
                    # if len(line.matched_debit_ids) == 0 and len(line.matched_credit_ids) == 0 and len(line.ctt_partial_reconcile_line_to_reconcile.matched_debit_ids) == 0 and len(line.ctt_partial_reconcile_line_to_reconcile.matched_credit_ids) == 0:
                    lines_to_reconcile += self.env['account.move.line'].search([('id','=',line.id)])
                    lines_to_reconcile += self.env['account.move.line'].search([('id','=',line.ctt_partial_reconcile_line_to_reconcile.id)])
                    lines_to_reconcile.reconcile()
                    line.ctt_partial_reconcile_line_to_reconcile = False
        lines_to_reconcile = self.env['account.move.line']     
        for line in self.line_ids:
            lines_to_reconcile += self.env['account.move.line'].search([('id','=',line.line_id.id)])
        lines_to_reconcile.reconcile()
        if len(move_lines) > 0:
            move.button_draft()
            move.button_cancel()
            
            
    

class ctt_partial_reconcile_wizard_line(models.TransientModel):
    _name = 'ctt_partial_reconcile.wizard.line'
    _description = "Líneas para Wizard para Conciliaciones parciales"
    
    wizard_id = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Asistente"
    )
    
    wizard_id_account_id = fields.Many2one(
        'account.account',
        string="Asistente - Cuenta Contable",
        related="wizard_id.account_id"
    )
    
    wizard_id_partner_id = fields.Many2one(
        'res.partner',
        string="Asistente - Contacto",
        related="wizard_id.partner_id"
    )
    
    wizard_id_1 = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Asistente opción 1"
    )
    
    wizard_id_1_account_id = fields.Many2one(
        'account.account',
        string="Asistente opción 1 - Cuenta Contable",
        related="wizard_id_1.account_id"
    )
    
    wizard_id_1_partner_id = fields.Many2one(
        'res.partner',
        string="Asistente opción 1 - Contacto",
        related="wizard_id_1.partner_id"
    )
    
    wizard_id_2 = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Asistente opción 2"
    )
    
    wizard_id_2_account_id = fields.Many2one(
        'account.account',
        string="Asistente opción 2 - Cuenta Contable",
        related="wizard_id_2.account_id"
    )
    
    wizard_id_2_partner_id = fields.Many2one(
        'res.partner',
        string="Asistente opción 2 - Contacto",
        related="wizard_id_2.partner_id"
    )
    
    @api.onchange('line_id')
    def onchange_line_id(self):
        for rec in self:
            rec.amount = rec.line_id.amount_residual
    
    line_id = fields.Many2one(
        'account.move.line',
        string="Apunte contable"
    )
    
    line_id_id = fields.Integer(
        string="Apunte contable - ID",
        related="line_id.id"
    )
    
    line_id_company_currency_id = fields.Many2one(
        string='Company Currency',
        related='line_id.move_id.company_currency_id', readonly=True, store=True, precompute=True,
    )
    
    line_id_debit = fields.Monetary(
        string='Débito',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.debit'
    )
    
    line_id_credit = fields.Monetary(
        string='Crédito',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.credit'
    )
    
    line_id_balance = fields.Monetary(
        string='Balance',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.balance'
    )
    
    line_id_amount_residual = fields.Monetary(
        string='Importe residual',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.amount_residual'
    )
    
    amount = fields.Float(
        string="Monto"
    )