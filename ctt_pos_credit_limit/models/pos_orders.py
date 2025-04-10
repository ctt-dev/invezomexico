# -*- coding: utf-8 -*-
"""Pos order"""
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Abhishek E T (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################

from odoo import models, api, fields

import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime


class PosOrderCreditLimit(models.Model):
    """Breaking the creation of credit payment journal"""
    # _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _inherit = ['pos.order','portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _name = "pos.order"

    paid_using_credit = fields.Boolean(string='Pagado con crédito', compute='_compute_paid_using_credit')
    can_modify_paid_credit = fields.Boolean(compute="_compute_modify_paid_credit", default=False)
    approve_credit_payment = fields.Boolean(string="Aprobar orden a credito", default=False)
    can_change_price = fields.Boolean(default=False, compute='_compute_can_change_price')

    @api.onchange('lines')
    def _onchange_products(self):
        for rec in self:
            _logger.warning(self)

    def _compute_paid_using_credit(self):
        for rec in self:
            pay_methods = rec.payment_ids.mapped('payment_method_id')
            rec.paid_using_credit = False
            if pay_methods:
                if pay_methods[0].is_credit:
                    rec.paid_using_credit = True

    def _compute_modify_paid_credit(self):
        for rec in self:
            if rec.env.user.allow_credit_sale:
                rec.can_modify_paid_credit = True
            else:
                rec.can_modify_paid_credit = False

    def _compute_can_change_price(self):
        for rec in self:
            if rec.env.user.change_price:
                rec.can_change_price = True
            else:
                rec.can_change_price = False
            
                

    def add_payment(self, data):
        """Create a new payment for the order"""
        self.ensure_one()
        payment_method = self.env['pos.payment.method'].search([
            ('id', '=', data['payment_method_id'])])
        if not payment_method.journal_id.pos_credit or payment_method.journal_id.id == self.env.ref('pos_credit_limit.credit_journal').id:
            self.env['pos.payment'].create(data)
            self.amount_paid = sum(self.payment_ids.mapped('amount'))


    @api.model
    def _order_fields(self, ui_order):
        vals = super(PosOrderCreditLimit,self)._order_fields(ui_order)
        if "approve_credit_payment" in ui_order:
            vals['approve_credit_payment'] = ui_order['approve_credit_payment']
        return vals
        
    @api.model
    def _export_for_ui(self, order):
        vals = super(PosOrderCreditLimit,self)._export_for_ui(order)
        vals['approve_credit_payment'] = order.approve_credit_payment
        return vals
