{
    'name': 'Búsquedas Masivas CTT',
    'author': "Mega",
    'website': "https://www.coreteam.mx",
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'summary': 'Búsqueda múltiple de órdenes de venta y facturas',
    'depends': ['sale', 'account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_mass_search_view.xml',
        'views/wizard_mass_search_invoice_view.xml',
        'views/wizard_mass_search_stock_picking.xml',
        'views/sale_order_extension_view.xml',
        'views/account_move_extension_view.xml',
        'views/stock_picking_estension_views.xml',
    ],
    'installable': True,
    'application': False,
    "assets": {
        "web.assets_backend": [
            'llantas_config/static/src/**/*',
        ],
    },    
}