# -*- coding: utf-8 -*-
{
    'name': "llantas_config",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'stock',
        'sale_management',
        'account',
        'hr',
        'l10n_mx_edi',
        'base_automation',
        'crm',
        'website',
        'account_accountant',
        'purchase',
        # 'purchase_stock',
        'website_sale',
        'mrp',
        'delivery',
        'fleet',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner.xml',
        'views/templates.xml',
        'views/views.xml',
        'views/catalogos.xml',
        'views/product.xml',
        'views/module.xml',
        'views/proveedores.xml',
        'views/subir_existencias.xml',
        'views/sales.xml',
        'views/marketplaces.xml',
        'views/stock.xml',
        'views/tablero_detallado.xml',
        'views/res.xml',
        'views/pagos_marketplace.xml',
        'views/detailed_sales.xml',
        'views/wizard_subir_existencias.xml',
        'reports/purchase.xml',
        'reports/Reporte_cotizacion_Racko.xml',
        # 'reports/new_invoice.xml',
        'views/account_move.xml',
        'reports/report_invoice.xml',
        'views/res_company.xml',
        'views/product_pricelist_item.xml',
        'views/purchase.xml',
        'reports/sale_order.xml',
        'reports/report_picking.xml',
        # 'views/style.css',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "assets": {
        "web.assets_backend": [
            'llantas_config/static/src/**/*',
        ],
    },    
}
