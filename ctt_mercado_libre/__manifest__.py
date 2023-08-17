# -*- coding: utf-8 -*-
{
    'name': "Conector Odoo / Mercado Libre",

    'summary': "Conector Odoo/Mercado Libre por CoreTeam Tech",

    'description': """
        Long description of module's purpose
    """,

    'author': "CoreTeam Tech",
    'website': "https://www.coreteam.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        # 'sale',
        'sale_management',
        'website_sale',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config.xml',
        'data/cron_verify_token.xml',
        'data/categories_import.xml',
        'data/mail_channel.xml',
        'views/product.xml',
        'views/categories.xml',
        'views/notify.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
