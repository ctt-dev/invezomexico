# -*- coding: utf-8 -*-
{
    'name': "Administrador de CFDI de proveedor",

    'summary': """""",

    'description': """""",

    'author': "CoreTeam Tech",
    'website': "https://www.coreteam.mx",
    'license': 'LGPL-3',
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'contacts',
        'account_accountant',
        'l10n_mx',
        'l10n_mx_edi',
        'l10n_mx_reports',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'data/ir_cron.xml',
        'data/mail_template.xml',
        'data/res_groups.xml',
        'views/account_move.xml',
        'views/l10n_mx_cfdi_document.xml',
        'views/l10n_mx_cfdi_request.xml',
        'views/l10n_mx_cfdi_fiel.xml',
        'views/res_company.xml',
        'views/wizard_l10n_mx_cfdi_document.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}
