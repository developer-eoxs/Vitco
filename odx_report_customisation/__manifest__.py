# -*- coding: utf-8 -*-
{
    'name': "Report Customisation",

    'summary': """
        Report Customisation""",

    'description': """
        
    """,

    'author': "OdoxSofthub",
    'website': "http://www.odoxsofthub.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'purchase', 'sale','web',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/due_reminder.xml',
        'security/security.xml',
        'reports/internal_layout.xml',
        'reports/commercial_invoice.xml',
        'reports/rfq_print.xml',
        'reports/purchase_order.xml',
        'reports/bol_so_report.xml',
        'reports/job_order.xml',
        'reports/production_order.xml',
        'reports/barcode.xml',
        'reports/mill_tc.xml',
        'views/views.xml',
    ],
}
