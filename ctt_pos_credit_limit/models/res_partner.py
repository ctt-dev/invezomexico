
from odoo import models, api, fields

import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime
from odoo.fields import Date

class ResPartnerCreditLimit(models.Model):
    """Overriding partner for setting credit and debit included in POS"""
    _inherit = 'res.partner'

    @api.model
    def _credit_search(self, operator, operand):
        return self._asset_difference_search('asset_receivable', operator, operand)

    @api.model
    def _debit_search(self, operator, operand):
        return self._asset_difference_search('liability_payable', operator, operand)

    warning_stage = fields.Float(
        string='Cantidad Alerta',
        compute='compute_active_limit',
        store=True, compute_sudo=True, readonly=False,
        help="Al superar esta cantidad arrojara una alerta",
        tracking=True,
    )

    credit = fields.Monetary(
        compute='_credit_debit_get', search=_credit_search,
        string='Total vencido', compute_sudo=True,
        help="Total amount this customer owes you.",
        groups='account.group_account_invoice,account.group_account_readonly',
        tracking=True,
    )

    debit = fields.Monetary(
        compute='_credit_debit_get', search=_debit_search, 
        string='Total Payable', compute_sudo=True,
        help="Total amount you have to pay to this vendor.",
        groups='account.group_account_invoice,account.group_account_readonly',
        tracking=True,
    )

    blocking_stage = fields.Float(
        string='Cantidad Bloqueo',
        compute='compute_active_limit',
        store=True, compute_sudo=True, readonly=False,
        help="Al superar esta cantidad no se permitirá hacer la venta a crédito",
        tracking=True,
    )

    credit_used = fields.Float(
        string='Crédito utilizado',
        compute='_credit_debit_get',
        store=True, compute_sudo=True, readonly=True
    )

    message_blocked_credit = fields.Text(
        string="Razón bloqueo de crédito", default="",
        readonly=False
    )

    active_limit = fields.Boolean(
        "Crédito Activo",
        compute='compute_active_limit',
        store=True, compute_sudo=True, readonly=False,
        default=False,
        tracking=True,
    )

    compute_limit = fields.Boolean(
        "Crédito Activo",
        compute='compute_active_limit',
        compute_sudo=True, readonly=False,
        default=False
    )

    required_oc = fields.Boolean(
        "Se requiere Orden de Compra en PdV?", default=False
    )

    postponements = fields.One2many(
        comodel_name='ctt_pos_credit_limit.debt_postponement',
        inverse_name='partner',
        string="Convenios de Deuda",
        tracking=True,
    )

    aplazo_actual = fields.Datetime(
        string="Convenio de deuda actual",
        compute="_compute_aplazo_actual"
    )

    can_block_credit = fields.Boolean(
        compute="_compute_block_credit", default=False
    )

    can_make_aplazo = fields.Boolean(
        compute="_compute_aplazo", default=False
    )

    def _compute_aplazo(self):
        for rec in self:
            rec.can_make_aplazo = rec.env.user.allow_aplazo
    def _compute_block_credit(self):
        for rec in self:
            rec.can_block_credit = rec.env.user.allow_credit_block

    @api.depends(
        'parent_id.active_limit', 'parent_id.warning_stage',
        'parent_id.blocking_stage', 'message_blocked_credit'
    )
    def compute_active_limit(self):
        _logger.warning("COMPUTE LIMIT")
        for partner in self:
            partner.compute_limit = False

            if not partner.message_blocked_credit:
                acc_move_not_paid = self.env['account.move'].search([
                    ('state', '=', 'posted'),
                    ('amount_residual', '>', 0.00),
                    ('payment_state', 'not in', ['paid', 'reversed', 'invoicing_legacy']),
                    ('partner_id', '=', partner.id)
                ])

                facturas_vencidas = any(
                    (acc.invoice_date_due - datetime.date.today()).days < -45
                    for acc in acc_move_not_paid
                )

                if facturas_vencidas:
                    partner.active_limit = False
                    partner.message_blocked_credit = "Facturas vencidas mayor a 45 días sin pagar"
                    return

            if not partner.message_blocked_credit:
                if partner.parent_id:
                    partner.active_limit = partner.parent_id.active_limit
                    partner.warning_stage = partner.parent_id.warning_stage
                    partner.blocking_stage = partner.parent_id.blocking_stage
                # No es necesario reasignar valores redundantes aquí

            else:
                acc_move_not_paid = self.env['account.move'].search([
                    ('state', '=', 'posted'),
                    ('amount_residual', '>', 0.00),
                    ('payment_state', 'not in', ['paid', 'reversed', 'invoicing_legacy']),
                    ('partner_id', '=', partner.id)
                ])

                facturas_pagadas = all(
                    (acc.invoice_date_due - datetime.date.today()).days > -45
                    for acc in acc_move_not_paid
                )

                if facturas_pagadas:
                    partner.active_limit = False
                    partner.message_blocked_credit = ""
                    return

                partner.active_limit = False


    @api.onchange('postponements')
    def _compute_aplazo_actual(self):
        for rec in self:
            rec.aplazo_actual = '1999-01-01'
            if rec.postponements:
                for post in rec.postponements:
                    if post.limit_date > rec.aplazo_actual:
                        rec.aplazo_actual = post.limit_date

    @api.depends_context('force_company', 'pos_order_ids.state')
    def _credit_debit_get(self):
        today = Date.today()

        for rec in self:
            super(ResPartnerCreditLimit, rec)._credit_debit_get()

            account_move_lines = rec.env['account.move.line'].search([
                ('parent_state', '=', 'posted'),
                ('account_type', '=', 'asset_receivable'),
                ('partner_id', '=', rec.id),
            ])

            # Crédito total utilizado (suma de todas las cuentas por cobrar pendientes)
            rec.credit_used = sum(account_move_lines.mapped('amount_residual'))

            # Crédito vencido (solo las que están vencidas)
            # rec.credit = sum(account_move_lines.filtered(lambda l: l.date_maturity < today).mapped('amount_residual'))
            rec.credit = sum(account_move_lines.filtered(lambda l: l.date_maturity and l.date_maturity < today).mapped('amount_residual'))


        # self.credit_used = 0
        # self.credit = 0
        # pos_orders = self.pos_order_ids.filtered(
        #     lambda x: x.partner_id and x.company_id == self.env.company and
        #               x.paid_using_credit == True and x.state in ('paid','done','invoiced')
        # )
        
        # for pos_order in pos_orders:
        #     amount_residue = 0
        #     credit_amount = pos_order.payment_ids
        #     _logger.warning(pos_order)
        #     #Falta validar credito pagado
        #     for amount in credit_amount:
        #         if amount.payment_method_id.is_credit:
        #             amount_residue = amount_residue + amount.amount
        #     if amount_residue != 0:
        #         pos_order.partner_id.credit += amount_residue
        #         pos_order.partner_id.credit_used += amount_residue

        # sale_orders = self.sale_order_ids.filtered(
        #     lambda x: x.partner_id and x.company_id == self.env.company and x.state in ('sale','done')
        # )
        
        # for sale_order in sale_orders:
        #     amount_residue = 0
        #     _logger.warning(sale_order)
        #     amount_residue = amount_residue + sale_order.amount_total
        #     if amount_residue != 0:
        #         sale_order.partner_id.credit += amount_residue
        #         sale_order.partner_id.credit_used += amount_residue

    deny_credit = fields.Boolean(
        string="Denegar credito",
        tracking=True
    )