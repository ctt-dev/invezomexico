/** @odoo-module **/
const {xml, Component, onWillStart,  useState} = owl;
import { useService } from '@web/core/utils/hooks';
import { standardFieldProps } from "@web/views/fields/standard_field_props";
// Import the registry
import {registry} from "@web/core/registry";

export class ProductSuppliersWidget extends Component {
    setup() {
        super.setup();

        console.log(this);
        console.log(this.props.value);
    }
}

ProductSuppliersWidget.template = 'llantas_config.productSuppliersWidget';

// Add the field to the correct category
registry.category("fields").add("product_suppliers", ProductSuppliersWidget)