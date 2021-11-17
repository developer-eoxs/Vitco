# -*- coding: utf-8 -*-
{
    'name': "Custom Receipt",

    'summary': """
        Custom Receipt""",

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
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'data/sequence.xml',
        'data/mail_template_for_approval.xml',
        'data/send_back_mail_template.xml',
        'views/acc_move_view.xml',
    ],
    
}
