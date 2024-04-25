/** @odoo-module **/
const {xml, Component, onWillStart,  useState} = owl;
import { useService } from '@web/core/utils/hooks';
import { standardFieldProps } from "@web/views/fields/standard_field_props";
// Import the registry
import {registry} from "@web/core/registry";

export class ProductSuppliersWidget extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');

        this.state = useState({
            lines: [],
            visible: false,
            totalExistencia: 0,
        });

        this.resId = this.props.record.resId;

        onWillStart(() => this.searchSupplierInfo(this.resId));
    }

    async searchSupplierInfo(resId) {
        const results = await this.orm.searchRead(
            'product.supplierinfo', 
            [["product_tmpl_id","=",resId]], 
            ["partner_id","existencia_actual","ultima_actualizacion","price","currency_id"]
        );
        const totalExistencia = results.reduce((acc, line) => acc + line.existencia_actual, 0);
        
        this.state.lines = results;
        this.state.visible = results.length > 0;
        this.state.totalExistencia = totalExistencia;
    }
}

ProductSuppliersWidget.template = 'llantas_config.productSuppliersWidget';

// Add the field to the correct category
registry.category("fields").add("product_suppliers", ProductSuppliersWidget)