# -*- coding: utf-8 -*-
{
    'name': "Conector Odoo / Walmart",

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
        'ctt_marketplaces'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/marketplace.xml',
        'data/cron_feed_status.xml',
        'views/marketplaces_template.xml',
        'wizard/wizard_category_install.xml',
        'views/res_config.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'post_init_hook': '_walmart_post_init',
}
