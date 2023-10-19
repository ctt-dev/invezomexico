# -*- coding: utf-8 -*-
{
    'name': "ctt_marketplaces",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'website_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config.xml',
        'views/product.xml',
        'views/marketplaces_template.xml',
        'views/marketplace.xml',
        'views/marketplaces_category.xml',
        'views/marketplaces_menuitems.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
