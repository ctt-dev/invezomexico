{
    'name': 'Búsquedas Masivas CTT',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Búsqueda múltiple de órdenes de venta y facturas',
    'depends': ['sale', 'account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_mass_search_view.xml',
        'views/wizard_mass_search_invoice_view.xml',
        'views/sale_order_extension_view.xml',
        'views/account_move_extension_view.xml',
        'views/stock_picking_estension_views.xml',
        'views/wizard_mass_seach_stock_picking.xml',
    ],
    'installable': True,
    'application': False,
}