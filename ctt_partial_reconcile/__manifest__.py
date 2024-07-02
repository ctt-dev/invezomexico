# -*- coding: utf-8 -*-
{
    'name': "Partial reconciliation",

    'summary': """""",

    'description': """
    """,

    'author': "Coreteam Tech",
    'website': "https://www.coreteam.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/ctt_partial_reconcile_wizard.xml',
        'views/res.xml',
    ],
}
