# -*- coding: utf-8 -*-

{
    'name': 'Steel Product Manufacturing',
    'category': 'Manufacturing',
    'sequence': 13,
    'summary': '',
    'author': 'Odox',
    'website': 'https://www.odoxsofthub.com',
    'version': '13.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','mrp'],

    # always loaded
    'data': [
        'views/mrp_wokorder_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
