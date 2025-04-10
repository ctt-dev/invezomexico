odoo.define('point_of_sale.RequireDiscountButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const SelectCashierCredit = require('point_of_sale.SelectCashierMixinInheritCreditLimit')
    const Registries = require('point_of_sale.Registries');
    const  pos_models = require("point_of_sale.models");
    const { isConnectionError } = require('point_of_sale.utils');

    class RequireDiscountButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            try {
                var order = this.env.pos.get_order()
                var selectCashierCredit = new SelectCashierCredit()
                var empleado = await selectCashierCredit.selectCashierCredit(0, this.env)
                if (empleado) {
                    console.log("Order Name:", order.name);
                    console.log("Cashier ID:", order.cashier.id);
                    console.log("Empleado ID:", empleado.id);
                    let approve_credit = await this.env.services.rpc(
                        {
                            model: 'pos.session',
                            method: 'require_approve_discount',
                            args: [[this.env.pos.pos_session.id], order.name, order.cashier.id, empleado.id]
                        },
                        { timeout: 3000, shadow: true }
                    );
                    console.log("Approval Result:", approve_credit);
                }
            } catch (e) {
                console.error("Error:", e);
                if (isConnectionError(e)) {
                    this.showPopup('OfflineErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('No se puede solicitar sin conexion a internet.'),
                    });
                }
            }
        }
    }
    RequireDiscountButton.template = 'RequireDiscountButton';

    ProductScreen.addControlButton({
        component: RequireDiscountButton,
    });

    Registries.Component.add(RequireDiscountButton);

    return RequireDiscountButton;
});
