# -*- coding: utf-8 -*-
{
    'name': "ctt_pos_credit_limit",

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
    'depends': ['base',
                'llantas_config',
                'hr',
               # 'pos_restaurant',
                'base_setup',
                'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        #'views/account_journal.xml',
        # 'views/pos_order.xml',
        'views/hr_employee.xml',
         'views/res.partner.xml',
        # 'views/pos_payment_method.xml',
        # 'views/pos_config.xml',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # 'assets': {
    #     'point_of_sale.pos_assets_backend': [
    #         'ctt_pos_credit_limit/static/src/js/*.js',
    #         'ctt_pos_credit_limit/static/src/scss/*.scss',
    #     ],
    #     'point_of_sale.assets': [
    #         'ctt_pos_credit_limit/static/src/xml/**/*.xml',
    #         'ctt_pos_credit_limit/static/src/scss/*.scss',
    #     ],
    # }
}
