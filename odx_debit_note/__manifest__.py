# -*- coding: utf-8 -*-
{
    'name': "Odx Debit Note",

    'summary': """
        Debit Note """,

    'description': """
    """,

    'author': "Odox",
    'website': "https://www.odoxsofthub.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','base_accounting_kit'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/payment_refund.xml',
        'views/views.xml',
        'views/journal_audit_report.xml',


    ],
}
