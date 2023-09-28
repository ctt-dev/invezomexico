# -*- coding: utf-8 -*-
{
    'name': "EFOS Manager",

    'summary': """""",

    'description': """""",

    'author': "CoreTeam Tech",
    'website': "https://www.coreteam.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'contacts',
        'purchase',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/res_config.xml',
        'data/res_groups.xml',
        'views/l10n_mx_efos.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
