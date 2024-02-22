# -*- coding: utf-8 -*-
{
    'name': "adrone_config",

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
        'website_sale',
        'mrp',
        'delivery',
        'industry_fsm',
        'llantas_config'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/catalogos.xml',
        # 'views/project_task.xml',
        'reports/formato_tareas.xml',
        'wizard/wizard_import_flight.info.xml',
        'views/flight_sheet.xml',
        'reports/report_invoices.xml',
        'views/sale.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
