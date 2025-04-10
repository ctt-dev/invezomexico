odoo.define(
    "point_of_sale.PartnerListScreenCredit", function(require) {
      "use strict";
      const PartnerListScreen = require('point_of_sale.PartnerListScreen');
      const PosComponent = require('point_of_sale.PosComponent');
      const Registries = require('point_of_sale.Registries');
      const NumberBuffer = require('point_of_sale.NumberBuffer');
      const selectDate = require('point_of_sale.SelectDate');
      var models = require('point_of_sale.models');
      var rpc = require('web.rpc');
      const PartnerListScreenCredit = (PartnerListScreen) =
          > class PartnerListScreenCredit extends PartnerListScreen {
        async clickPartner(partner) {
          if (this.state.selectedPartner&& this.state.selectedPartner.id ==
              = partner.id) {
            this.state.selectedPartner = null;
          } else {
            if (partner && this.env.pos.synch.status == 'connected') {
              let partners = await this.env.services.rpc({
                model : 'pos.session',
                method : 'get_partner_credit',
                args : [ [odoo.pos_session_id], partner.id ],
              },
                                                         {
                                                           timeout : 3000,
                                                           shadow : true,
                                                         }) 
              var credit = partners.split("/") 
              partner.credit_used = parseFloat(credit[0])
              partner.aplazo_actual = credit[1]
              partner.active_limit = (credit[2]=="True")?true:false
            }
            this.state.selectedPartner = partner;
          }
          this.confirm();
        }
      } 
    Registries.Component.extend(PartnerListScreen, PartnerListScreenCredit);
      return PartnerListScreen;
    });