# -*- coding: utf-8 -*-
{
    'name': "Partial reconciliation",
    'summary': """Partial reconciliation wizard for accounting""",
    'description': """
        Allows partial reconciliation of journal items
    """,
    'author': "Coreteam Tech",
    'website': "https://www.coreteam.mx",
    'license': 'LGPL-3',
    'category': 'Accounting',
    'version': '19.0.1.0.0',  # Cambia a versión compatible con Odoo 17/18/19

    # depends corregidos para Odoo 19
    'depends': [
        'base',
        'account',
        # 'account_accountant' ya no existe en Odoo 19
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/ctt_partial_reconcile_wizard.xml',
        'views/res.xml',
    ],
}