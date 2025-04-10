odoo.define('ctt_credit_limit.CreditOrder', function(require) {
  'use strict';
  var {Order} = require('point_of_sale.models');
  const Registries = require('point_of_sale.Registries');
  var PosDB = require('point_of_sale.DB');
  var config = require('web.config');
  const {markRaw, reactive} = owl;
  const CreditOrder = (Order) => class CreditOrder extends Order {
    constructor(obj, options) {
      super(...arguments);
      this.approve_credit_payment = this.approve_credit_payment || options.approve_credit_payment
    }
    init_from_JSON(json) {
      super.init_from_JSON(...arguments);
      this.approve_credit_payment = json.approve_credit_payment
    }
    export_as_JSON() {
      const json = super.export_as_JSON(...arguments);
      json.approve_credit_payment = this.approve_credit_payment;
      return json;
    }
  }
  Registries.Model.extend(Order, CreditOrder);
});