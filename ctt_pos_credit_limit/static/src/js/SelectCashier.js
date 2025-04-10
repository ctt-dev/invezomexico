odoo.define(
  'point_of_sale.SelectCashierMixinInheritCreditLimit',
  function (require) {
    'use strict'
    const SelectCashierMixinCreditLimit = require('point_of_sale.SelectCashierMixinCreditLimit')
    const PosComponent = require('point_of_sale.PosComponent')
    const { useListener } = require('@web/core/utils/hooks')
    const Registries = require('point_of_sale.Registries')
    const pos_models = require('point_of_sale.models')
    const NumberBuffer = require('point_of_sale.NumberBuffer')
    class SelectCashierMixinInheritCreditLimit extends SelectCashierMixinCreditLimit(
      PosComponent
    ) {
      setup () {
        super.setup()
        useBarcodeReader({ cashier: this.barcodeCashierAction }, true)
      }
      async askPin (employee) {
        const { confirmed, payload: inputPin } = await this.showPopup(
          'NumberPopup',
          {
            isPassword: true,
            title: this.env._t('Password ?'),
            startingValue: null
          }
        )
        if (!confirmed) return
        if (employee.pin === Sha1.hash(inputPin)) {
          return employee
        } else {
          await this.showPopup('ErrorPopup', {
            title: this.env._t('Incorrect Password')
          })
          return
        }
      }
      async askPin (employee, price) {
        const { confirmed, payload: inputPin } = await this.showPopup(
          'NumberPopup',
          {
            isPassword: true,
            title: this.env._t('Password ?'),
            startingValue: null
          }
        )
        if (!confirmed) return
        if (employee.pin === Sha1.hash(inputPin)) {
          console.log(employee)
          console.log(price)
          return employee
        } else {
          await this.showPopup('ErrorPopup', {
            title: this.env._t('Incorrect Password')
          })
          return
        }
      }
      async selectCashier () {
        if (this.env.pos.config.module_pos_hr) {
          const employeesList = this.env.pos.employees
            .filter(employee => employee.id !== this.env.pos.get_cashier().id)
            .map(employee => {
              return {
                id: employee.id,
                item: employee,
                label: employee.name,
                isSelected: false
              }
            })
          let { confirmed, payload: employee } = await this.showPopup(
            'SelectionPopup',
            { title: this.env._t('Change Cashier'), list: employeesList }
          )
          if (!confirmed) {
            return
          }
          if (employee && employee.pin) {
            employee = await this.askPin(employee)
          }
          if (employee) {
            this.env.pos.set_cashier(employee)
          }
          return employee
        }
      }

    async selectCashierCredit (price, env) {
        this.env = env
    if (this.env.pos.config.module_pos_hr) {
      const employeesList = this.env.pos.approbation_employees
        .filter(employee => employee.id !== this.env.pos.get_cashier().id)
        .map(employee => {
          return {
            id: employee.id,
            item: employee,
            label: employee.name,
            isSelected: false
          }
        })
      let { confirmed, payload: employee } = await this.showPopup(
        'SelectionPopup',
        { title: this.env._t('Selecciona empleado'), list: employeesList }
      )
      if (!confirmed) {
        return
      } 
      return employee
    }
  }
      async selectCashierAplazoDeuda (price, env) {
        this.env = env
          var confirmed = true
          var employee = undefined
          var tupla = undefined
        if (this.env.pos.config.module_pos_hr) {
            if(!this.env.pos.get_cashier.allow_aplazo){
                  const employeesList = this.env.pos.employees
                    .filter(employee => employee.id !== this.env.pos.get_cashier().id)
                    .filter(employee => employee.allow_aplazo === true)
                    .map(employee => {
                      return {
                        id: employee.id,
                        item: employee,
                        label: employee.name,
                        isSelected: false
                      }
                    })
                 tupla = await this.showPopup(
                    'SelectionPopup',
                    {
                      title: this.env._t('Autorizar Convenio de Deuda'),
                      list: employeesList
                    }
                  )
                employee = tupla.payload
                confirmed = tupla.confirmed
            }else{
                confirmed = true
                employee = this.env.pos.get_cashier
            }
          if (!confirmed) {
            return
          }
          if (employee && employee.pin) {
            employee = await this.askPin(employee, price)
          }
          if (employee) {
          }
          return employee
        }
      }
    }
    Registries.Component.add(SelectCashierMixinInheritCreditLimit)
    return SelectCashierMixinInheritCreditLimit
  }
)
