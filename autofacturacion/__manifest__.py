# -*- coding: utf-8 -*-
{
    'name': "autofacturacion",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base',
               'sale',
               'l10n_latam_invoice_document',
               'l10n_latam_base',],

    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/autofacturacion.xml',
        'views/autofacturacionForm.xml',
        'views/timbrar.xml',
        'views/error.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],

}
