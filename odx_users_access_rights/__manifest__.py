# -*- coding: utf-8 -*-

{
    'name': 'Odx Users Access Rights',
    'category': 'Sale',
    'sequence': 13,
    'summary': '',
    'author': 'Odox',
    'website': 'https://www.odoxsofthub.com',
    'version': '13.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_users_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
