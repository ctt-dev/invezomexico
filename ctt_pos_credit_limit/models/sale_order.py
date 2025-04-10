from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, date
# from datetime import datetime

class SaleOrderCreditLimit(models.Model):
    _inherit = 'sale.order'

    require_oc = fields.Boolean(compute="onchange_partner_warning")

    # def action_confirm(self):
    #     today_date = datetime.today().date()
    #     aplazo = (self.partner_id.aplazo_actual or today_date).date()
    
    #     # Bloqueo manual del crédito
    #     if self.partner_id.deny_credit and self.payment_term_id.name != 'Pago de contado':
    #         raise UserError("Crédito de cliente bloqueado manualmente. Por favor, revise con cobranza.")
    
    #     # Validar facturas vencidas
    #     overdue_invoices = self.env['account.move'].search([
    #         ('partner_id', '=', self.partner_id.id),
    #         ('payment_state', 'in', ['not_paid', 'partial']),
    #         ('state', '=', 'posted'),
    #         ('move_type', '=', 'out_invoice'),
    #         ('invoice_date_due', '<', today_date)
    #     ])
    #     if overdue_invoices and (not self.partner_id.aplazo_actual or aplazo < today_date):
    #         invoice_details = "\n".join([
    #             f"{inv.name}, Monto: ${inv.amount_total}, Días vencidos: {(today_date - inv.invoice_date_due).days}"
    #             for inv in overdue_invoices
    #         ])
    #         raise UserError(f"El cliente tiene las siguientes facturas vencidas:\n{invoice_details}\n\nContacte a cobranza.")
    
    #     # Mensaje de aplazo vigente
    #     if aplazo >= today_date:
    #         formatted_aplazo = aplazo.strftime("%d-%m-%Y")
    #         self.message_post(body=f"El cliente tiene un aplazo vigente hasta el: {formatted_aplazo}\n\nPuede continuar.")
    
    #     # Validar límite de crédito
    #     if self.partner_id.active_limit:
    #         # Calcular el total de órdenes de venta activas no facturadas
    #         active_orders = self.env['sale.order'].search([
    #             ('partner_id', '=', self.partner_id.id),
    #             ('state', 'in', ['sale', 'done']),  # Estados relevantes para órdenes confirmadas
    #             ('invoice_status', '!=', 'invoiced')  # Excluir las ya facturadas
    #         ])
    #         active_orders_total = sum(order.amount_total for order in active_orders)
    
    #         # Calcular el crédito total utilizado
    #         total_credit_used = self.partner_id.credit_used + self.amount_total + active_orders_total
    
    #         # Validar si el crédito utilizado supera el límite
    #         if total_credit_used > self.partner_id.blocking_stage and aplazo < today_date:
    #             raise UserError(
    #                 f"El cliente ha superado su límite de crédito.\n"
    #                 f"Crédito utilizado (incluyendo órdenes activas): ${total_credit_used:.2f}\n"
    #                 f"Límite de crédito: ${self.partner_id.blocking_stage:.2f}."
    #             )
    
    #         # Advertencia si está cerca del límite de crédito
    #         remaining_credit = self.partner_id.blocking_stage - total_credit_used
    #         if remaining_credit < 1500:
    #             self.message_post(body=(
    #                 f"El cliente está cerca de superar su límite de crédito.\n"
    #                 f"Crédito utilizado (incluyendo órdenes activas): ${total_credit_used:.2f}\n"
    #                 f"Límite de crédito: ${self.partner_id.blocking_stage:.2f}."
    #             ))
    
    #     # Validar si se requiere una OC
    #     if self.partner_id.required_oc and not self.client_order_ref:
    #         raise UserError("El cliente requiere una orden de compra (OC).")
    
    #     return super(SaleOrderCreditLimit, self).action_confirm()

        
    def action_confirm(self):
        today_date = datetime.today().date()
        aplazo = (self.partner_id.aplazo_actual or today_date).date()
    
        # Bloqueo manual del crédito
        if self.partner_id.deny_credit and self.payment_term_id.name != 'Pago de contado':
            raise UserError("Crédito de cliente bloqueado manualmente. Por favor, revise con cobranza.")
    
        # Validar facturas vencidas
        overdue_invoices = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('invoice_date_due', '<', today_date)
        ])
        if overdue_invoices and (not self.partner_id.aplazo_actual or aplazo < today_date):
            invoice_details = "\n".join([
                f"{inv.name}, Monto: ${inv.amount_total}, Días vencidos: {(today_date - inv.invoice_date_due).days}"
                for inv in overdue_invoices
            ])
            raise UserError(f"El cliente tiene las siguientes facturas vencidas:\n{invoice_details}\n\nContacte a cobranza.")
    
        # Mensaje de aplazo vigente
        if aplazo >= today_date:
            formatted_aplazo = aplazo.strftime("%d-%m-%Y")
            self.message_post(body=f"El cliente tiene un aplazo vigente hasta el: {formatted_aplazo}\n\nPuede continuar.")
    
        # Validar límite de crédito basado solo en facturas
        if self.partner_id.active_limit:
            # Calcular el crédito total utilizado basado en facturas pendientes de pago
            open_invoices = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice')
            ])
            total_credit_used = sum(inv.amount_total for inv in open_invoices) + self.amount_total
    
            # Validar si el crédito utilizado supera el límite
            if total_credit_used > self.partner_id.blocking_stage and aplazo < today_date:
                raise UserError(
                    f"El cliente ha superado su límite de crédito.\n"
                    f"Crédito utilizado: ${total_credit_used:.2f}\n"
                    f"Límite de crédito: ${self.partner_id.blocking_stage:.2f}."
                )
    
            # Advertencia si está cerca del límite de crédito
            remaining_credit = self.partner_id.blocking_stage - total_credit_used
            if remaining_credit < 1500:
                self.message_post(body=(
                    f"El cliente está cerca de superar su límite de crédito.\n"
                    f"Crédito utilizado: ${total_credit_used:.2f}\n"
                    f"Límite de crédito: ${self.partner_id.blocking_stage:.2f}."
                ))
    
        # Validar si se requiere una OC
        if self.partner_id.required_oc and not self.client_order_ref:
            raise UserError("El cliente requiere una orden de compra (OC).")
    
        return super(SaleOrderCreditLimit, self).action_confirm()
        
    @api.onchange('partner_id')
    def onchange_partner_warning(self):
        self.require_oc = self.partner_id.required_oc

        # Obtener la fecha de aplazo
        aplazo = self.partner_id.aplazo_actual or datetime(1999, 1, 1).date()
        if isinstance(aplazo, datetime):
            aplazo = aplazo.date()

        # Fecha y hora actual ajustada al huso horario (UTC -7)
        today_date = (datetime.now() - timedelta(hours=7)).date()

        # Verificación de facturas vencidas
        overdue_invoices = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('invoice_date_due', '<', today_date)
        ])

        if overdue_invoices and (not self.partner_id.aplazo_actual or aplazo < today_date):
            invoice_details = [
                f"{inv.name}, Monto: ${inv.amount_total}, Días vencidos: {(today_date - inv.invoice_date_due).days}"
                for inv in overdue_invoices
            ]
            details_message = "\n".join(invoice_details)
            return {
                'warning': {
                    'title': _("Facturas vencidas para %s" % self.partner_id.name),
                    'message': "El cliente tiene las siguientes facturas vencidas:\n" + details_message + 
                               "\n\nContacte a cobranza.",
                }
            }

        # Verificación de bloqueo de crédito
        if self.partner_id.message_blocked_credit and aplazo < today_date:
            return {
                'warning': {
                    'title': _("Crédito bloqueado para %s" % self.partner_id.name),
                    'message': "El cliente tiene su crédito bloqueado por la siguiente razón:\n" +
                               self.partner_id.message_blocked_credit,
                }
            }

        # Verificación de aplazo vigente
        if aplazo >= today_date:
            formatted_aplazo = aplazo.strftime("%d-%m-%Y")
            return {
                'warning': {
                    'title': _("Aplazo vigente para %s" % self.partner_id.name),
                    'message': "El cliente tiene un aplazo vigente hasta el: {}\n\nPuede continuar...".format(formatted_aplazo),
                }
            }

        # Verificación del límite de crédito
        if self.partner_id.active_limit:
            if self.partner_id.credit_used > self.partner_id.blocking_stage and aplazo < today_date:
                return {
                    'warning': {
                        'title': _("Límite de crédito excedido para %s" % self.partner_id.name),
                        'message': "El cliente ha superado su límite de crédito.\n\n"
                                   "Crédito utilizado: ${:.2f}\n"
                                   "Límite de crédito: ${:.2f}".format(
                                       self.partner_id.credit_used, self.partner_id.blocking_stage
                                   ),
                    }
                }

            elif self.partner_id.blocking_stage - self.partner_id.credit_used < 1500:
                return {
                    'warning': {
                        'title': _("Advertencia de crédito para %s" % self.partner_id.name),
                        'message': "El cliente está cerca de su límite de crédito.\n\n"
                                   "Crédito utilizado: ${:.2f}\n"
                                   "Límite de crédito: ${:.2f}".format(
                                       self.partner_id.credit_used, self.partner_id.blocking_stage
                                   ),
                    }
                }
