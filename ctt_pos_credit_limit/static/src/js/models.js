odoo.define('point_of_sale.employees_credit', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosHrPosGlobalState2 = (PosGlobalState) => class PosHrPosGlobalState2 extends PosGlobalState {
    
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.module_pos_hr) {
            this.approbation_employees = loadedData['approbation.hr.employee'];
            this.approbation_employee_by_id = loadedData['approbation_employee_by_id'];
            this.reset_cashier();
        }
    }
  }
  Registries.Model.extend(PosGlobalState, PosHrPosGlobalState2);
});