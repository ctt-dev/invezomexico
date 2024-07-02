# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import datetime
import pytz
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


class ctt_partial_reconcile_wizard(models.TransientModel):
    _name = 'ctt_partial_reconcile.wizard' 
    _description = "Wizard for partial reconciliation"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        account_id_list = []
        partner_id_list = []
        move_line_ids = self.env['account.move.line'].browse(self.env.context.get('active_ids'))
        wizard_lines = []
        for move_line_id in move_line_ids:
            if move_line_id.account_id.id not in account_id_list:
                account_id_list.append(move_line_id.account_id.id)
            if move_line_id.partner_id.id not in partner_id_list:
                partner_id_list.append(move_line_id.partner_id.id)
            wizard_lines.append((0, 0, {
                'wizard_id': self.id,
                'line_id': move_line_id.id,
                'amount': 0,
            }))
        if len(account_id_list) == 1:
            res['account_id'] = account_id_list[0]
        elif len(account_id_list) > 1:
            raise UserError(_("You can only select journal items from one account."))
        if len(partner_id_list) == 1:
            res['partner_id'] = partner_id_list[0]
            res['line_ids_opc_1'] = wizard_lines
        else:
            res['line_ids_opc_2'] = wizard_lines
        return res
    
    @api.onchange('type')
    def onchange_type(self):
        if self.wizard_origin == "menu_item":
            self.account_id = False
            self.line_ids = False
            self.line_ids_opc_1 = False
            self.line_ids_opc_2 = False
    
    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.wizard_origin == "menu_item":
            self.line_ids = False
            self.line_ids_opc_1 = False
            self.line_ids_opc_2 = False
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.wizard_origin == "menu_item":
            self.line_ids = False
            self.line_ids_opc_1 = False
            self.line_ids_opc_2 = False

    wizard_origin = fields.Selection(
        [
            ('menu_item','menu_item'),
            ('account_move_lines','account_move_lines')
        ],
        default="menu_item",
        string="Wizard origin"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner"
    )
    
    type = fields.Selection(
        [
            ('asset_receivable','Receivable'),
            ('liability_payable','Payable'),
        ],
        string="Account type",
        default="asset_receivable",
        required=1
    )
    
    account_id = fields.Many2one(
        'account.account',
        string="Account",
    )
    
    line_ids = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id',
        string="Journal items to reconcile"
    )
    
    line_ids_opc_1 = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id_1',
        string="Journal items to reconcile - Option 1"
    )
    
    line_ids_opc_2 = fields.One2many(
        'ctt_partial_reconcile.wizard.line',
        'wizard_id_2',
        string="Journal items to reconcile - Option 2"
    )
    
    def reconcile(self):
        if len(self.line_ids_opc_1) > 0:
            self.line_ids = self.line_ids_opc_1
        if len(self.line_ids_opc_2) > 0:
            self.line_ids = self.line_ids_opc_2
            
        if self.env.company.ctt_partial_reconcile_journal_id.id == False:
            raise UserError(_("It is necessary to specify a Journal for partial reconcile entries in the company. Configure it to continue..."))
        if len(self.line_ids) < 2:
            raise UserError(_("You must include at least 2 journal items in order to continue..."))
        check_list = []
        for line in self.line_ids:
            if round(line.amount,2) == 0:
                raise UserError(_("You must NOT include lines with an amount of 0.00. Delete them to continue..."))
            if line.line_id.id in check_list:
                raise UserError(_("You should NOT include 2 times the same journal item for reconciliation..."))
            if line.line_id.id not in check_list:
                check_list.append(line.line_id.id)
        total_amount = 0
        for line in self.line_ids:
            total_amount += line.amount
        if round(total_amount,2) != 0:
            raise UserError(_("The total amount must be 0.00 to continue..."))
        
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
    _description = "Wizard for partial reconciliation lines"
    
    wizard_id = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Wizard"
    )
    
    wizard_id_account_id = fields.Many2one(
        'account.account',
        string="Wizard - Account",
        related="wizard_id.account_id"
    )
    
    wizard_id_partner_id = fields.Many2one(
        'res.partner',
        string="Wizard - Partner",
        related="wizard_id.partner_id"
    )
    
    wizard_id_1 = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Wizard option 1"
    )
    
    wizard_id_1_account_id = fields.Many2one(
        'account.account',
        string="Wizard option 1 - Account",
        related="wizard_id_1.account_id"
    )
    
    wizard_id_1_partner_id = fields.Many2one(
        'res.partner',
        string="Wizard option 1 - Partner",
        related="wizard_id_1.partner_id"
    )
    
    wizard_id_2 = fields.Many2one(
        'ctt_partial_reconcile.wizard',
        string="Wizard option 2"
    )
    
    wizard_id_2_account_id = fields.Many2one(
        'account.account',
        string="Wizard option 2 - Account",
        related="wizard_id_2.account_id"
    )
    
    wizard_id_2_partner_id = fields.Many2one(
        'res.partner',
        string="Wizard option 2 - Partner",
        related="wizard_id_2.partner_id"
    )
    
    @api.onchange('line_id')
    def onchange_line_id(self):
        for rec in self:
            rec.amount = rec.line_id.amount_residual
    
    line_id = fields.Many2one(
        'account.move.line',
        string="Journal item"
    )
    
    line_id_id = fields.Integer(
        string="Journal item - ID",
        related="line_id.id"
    )
    
    line_id_company_currency_id = fields.Many2one(
        string='Company Currency',
        related='line_id.move_id.company_currency_id', readonly=True, store=True, precompute=True,
    )
    
    line_id_debit = fields.Monetary(
        string='Debit',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.debit'
    )
    
    line_id_credit = fields.Monetary(
        string='Credit',
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
        string='Residual amount',
        store=True,
        currency_field='line_id_company_currency_id',
        related='line_id.amount_residual'
    )
    
    amount = fields.Float(
        string="Amount"
    )