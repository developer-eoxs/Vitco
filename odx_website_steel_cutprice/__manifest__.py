# -*- coding: utf-8 -*-

{
    'name': 'Website Steel Cut Price',
    'category': 'Website',
    'version': '13.0.0.0',
    'sequence': 14,
    'summary': '',
    'author': 'Odox SoftHub/Fathima',
    'website': 'https://www.odoxsofthub.com',

    # any module necessary for this one to work correctly
    'depends': ['website', 'website_sale','sale'],

    # always loaded
    'data': [

        'views/assets.xml',
        'views/templates.xml',



    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
