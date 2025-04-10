odoo.define('point_of_sale.CreditLimitPaymentScreen', function (require) {
  'use strict'
  const PaymentScreen = require('point_of_sale.PaymentScreen')
  const PosComponent = require('point_of_sale.PosComponent')
  const SelectCashierCredit = require('point_of_sale.SelectCashierMixinInheritCreditLimit')
  const Registries = require('point_of_sale.Registries')
  const NumberBuffer = require('point_of_sale.NumberBuffer')
  const selectDate = require('point_of_sale.SelectDate')
  var models = require('point_of_sale.models')
  var rpc = require('web.rpc')
  const CreditDetails = PaymentScreen =>
    class CreditDetails extends PaymentScreen {
      addNewPaymentLine ({ detail: paymentMethod }) {
       if(this.currentOrder.get_partner() && paymentMethod.is_credit && this.currentOrder.get_partner().deny_credit){
              this.showPopup('ErrorPopup', {
                title: this.env._t('Crédito de cliente bloqueado manualmente'),
                body: this.env._t(
                  'Para mas informacíon revise con cobranza'
                )
              })
              return false
       }
        var self = this
        var current_order = this.currentOrder
        var credit_journal = false
        var partner = this.currentOrder.get_partner()
        var due = this.currentOrder.get_due()
        current_order.add_paymentline(paymentMethod)
      }
      async selectPartner () {
        const currentPartner = this.currentOrder.get_partner()
        const { confirmed, payload: newPartner } = await this.showTempScreen(
          'PartnerListScreen',
          { partner: currentPartner }
        )
        if (confirmed) {
          if (newPartner && this.env.pos.synch.status == 'connected') {
            let partners = await this.env.services.rpc(
              {
                model: 'pos.session',
                method: 'get_partner_credit',
                args: [[odoo.pos_session_id], newPartner.id]
              },
              { timeout: 3000, shadow: true }
            )
            var credit = partners.split('/')
            newPartner.credit_used = parseFloat(credit[0])
            newPartner.aplazo_actual = credit[1]
          }
          this.currentOrder.set_partner(newPartner)
          this.currentOrder.updatePricelist(newPartner)
        }
      }
      async _isOrderValid (isForceValidate) {
        var self = this
        var order = this.env.pos.get_order()
        if (
          this.currentOrder.get_orderlines().length === 0 &&
          this.currentOrder.is_to_invoice()
        ) {
          this.showPopup('ErrorPopup', {
            title: this.env._t('Empty Order'),
            body: this.env._t(
              'There must be at least one product in your order before it can be validated and invoiced.'
            )
          })
          return false
        }
        const splitPayments = this.paymentLines.filter(
          payment => payment.payment_method.split_transactions
        )
        if (splitPayments.length && !this.currentOrder.get_partner()) {
          const paymentMethod = splitPayments[0].payment_method
          const { confirmed } = await this.showPopup('ConfirmPopup', {
            title: this.env._t('Customer Required'),
            body: _.str.sprintf(
              this.env._t('Customer is required for %s payment method.'),
              paymentMethod.name
            )
          })
          if (confirmed) {
            this.selectPartner()
          }
          return false
        }
        if (
          (this.currentOrder.is_to_invoice() ||
            this.currentOrder.is_to_ship()) &&
          !this.currentOrder.get_partner()
        ) {
          const { confirmed } = await this.showPopup('ConfirmPopup', {
            title: this.env._t('Please select the Customer'),
            body: this.env._t(
              'You need to select the customer before you can invoice or ship an order.'
            )
          })
          if (confirmed) {
            this.selectPartner()
          }
          return false
        }
        for (var i = 0; i < order.paymentlines.length; i++) {
          var credit_journal = false
          if (order.paymentlines[i].payment_method.is_credit) {
            credit_journal = true
          }
          if (credit_journal && !order.partner.deny_credit) {
            if (order.partner.active_limit) {
              let approve_credit = await this.env.services.rpc(
                {
                  model: 'pos.session',
                  method: 'validate_approve_credit',
                  args: [[odoo.pos_session_id], order.name]
                },
                { timeout: 3000, shadow: true }
              )
              order.approve_credit_payment = approve_credit
              if (!order.approve_credit_payment) {
                var temp_credit = order.partner.credit_used
                temp_credit += order.paymentlines[i].amount
                if (order.partner.blocking_stage >= temp_credit) {
                  if (order.partner.warning_stage <= temp_credit) {
                    alert(
                      'Esta excediendo la cantidad de alerta de crédito utilizado.\n\n Crédito Actual is : ' +
                        order.partner.credit_used +
                        '.\n\n Límite de Crédito : ' +
                        order.partner.blocking_stage +
                        ''
                    )
                  }
                  order.partner.credit_used = temp_credit
                } else {
                  if (new Date(order.partner.aplazo_actual) < new Date()) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                      title: this.env._t('Excediendo límite de crédito'),
                      body: this.env._t(
                        [
                          'El cliente ha excedido su crédito(Límite de Crédito :' +
                            order.partner.blocking_stage +
                            ').',
                          '\nCredito Actual(' +
                            order.partner.credit_used +
                            ').',
                          '¿Desea aplazar la deuda del cliente?'
                        ].join(' ')
                      )
                    })
                    if (confirmed) {
                      console.log('elegir fecha')
                      var selectDatePop = new selectDate()
                      const fecha = await selectDatePop.setDate(this)
                      if (fecha[0]) {
                        var selectCashierCredit = new SelectCashierCredit()
                        if (!this.env.pos.cashier.allow_aplazo) {
                          var empleado =
                            await selectCashierCredit.selectCashierAplazoDeuda(
                              0,
                              this.env
                            )
                          if (empleado) {
                            let partners = await this.env.services.rpc(
                              {
                                model: 'pos.session',
                                method: 'create_postponement',
                                args: [
                                  [odoo.pos_session_id],
                                  order.partner.id,
                                  fecha[0],
                                  fecha[1],
                                  this.env.pos.cashier.id,
                                  empleado.id
                                ]
                              },
                              { timeout: 3000, shadow: true }
                            )
                            order.partner.aplazo_actual = fecha
                          } else {
                            return false
                          }
                        } else {
                          let partners = await this.env.services.rpc(
                            {
                              model: 'pos.session',
                              method: 'create_postponement',
                              args: [
                                [odoo.pos_session_id],
                                order.partner.id,
                                fecha[0],
                                fecha[1],
                                this.env.pos.cashier.id,
                                this.env.pos.cashier.id
                              ]
                            },
                            { timeout: 3000, shadow: true }
                          )
                          order.partner.aplazo_actual = fecha
                        }
                      }else{
                        return false
                      }
                    } else {
                      return false
                    }
                  }
                }
              }
            } else {
              self.showPopup('ErrorPopup', {
                title: self.env._t('El cliente no cuenta con crédito activo'),
                body: self.env._t(
                  'Contacte a un administrador para activar su crédito'
                )
              })
              return false
            }
          }
            else if(credit_journal && order.partner.deny_credit) {
              self.showPopup('ErrorPopup', {
                title: self.env._t('Crédito de cliente bloqueado manualmente'),
                body: self.env._t(
                  'Para mas informacíon revise con cobranza'
                )
              })
              return false
          }
        }
        let partner = this.currentOrder.get_partner()
        if (
          this.currentOrder.is_to_ship() &&
          !(
            partner.name &&
            partner.street &&
            partner.city &&
            partner.country_id
          )
        ) {
          this.showPopup('ErrorPopup', {
            title: this.env._t('Incorrect address for shipping'),
            body: this.env._t('The selected customer needs an address.')
          })
          return false
        }
        if (
          this.currentOrder.get_total_with_tax() != 0 &&
          this.currentOrder.get_paymentlines().length === 0
        ) {
          this.showNotification(
            this.env._t('Select a payment method to validate the order.')
          )
          return false
        }
        if (!this.currentOrder.is_paid() || this.invoicing) {
          return false
        }
        if (this.currentOrder.has_not_valid_rounding()) {
          var line = this.currentOrder.has_not_valid_rounding()
          this.showPopup('ErrorPopup', {
            title: this.env._t('Incorrect rounding'),
            body: this.env._t(
              'You have to round your payments lines.' +
                line.amount +
                ' is not rounded.'
            )
          })
          return false
        }
        if (
          Math.abs(
            this.currentOrder.get_total_with_tax() -
              this.currentOrder.get_total_paid() +
              this.currentOrder.get_rounding_applied()
          ) > 0.00001
        ) {
          var cash = false
          for (var i = 0; i < this.env.pos.payment_methods.length; i++) {
            cash = cash || this.env.pos.payment_methods[i].is_cash_count
          }
          if (!cash) {
            this.showPopup('ErrorPopup', {
              title: this.env._t(
                'Cannot return change without a cash payment method'
              ),
              body: this.env._t(
                'There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'
              )
            })
            return false
          }
        }
        if (
          !isForceValidate &&
          this.currentOrder.get_total_with_tax() > 0 &&
          this.currentOrder.get_total_with_tax() * 1000 <
            this.currentOrder.get_total_paid()
        ) {
          this.showPopup('ConfirmPopup', {
            title: this.env._t('Please Confirm Large Amount'),
            body:
              this.env._t('Are you sure that the customer wants to  pay') +
              ' ' +
              this.env.pos.format_currency(this.currentOrder.get_total_paid()) +
              ' ' +
              this.env._t('for an order of') +
              ' ' +
              this.env.pos.format_currency(
                this.currentOrder.get_total_with_tax()
              ) +
              ' ' +
              this.env._t('? Clicking "Confirm" will validate the payment.')
          }).then(({ confirmed }) => {
            if (confirmed) this.validateOrder(true)
          })
          return false
        }
        if (!this.currentOrder._isValidEmptyOrder()) return false
        return true
      }
    }
  Registries.Component.extend(PaymentScreen, CreditDetails)
  return PaymentScreen
})
