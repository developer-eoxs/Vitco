# -*- coding: utf-8 -*-

{
    'name': 'Odx Freight Management',
    'category': 'Purchase',
    'sequence': 13,
    'summary': '',
    'author': 'Odox',
    'website': 'https://www.odoxsofthub.com',
    'version': '13.0.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mail', 'purchase','account','sale','odx_steel_production','odx_product_custom_steel'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mode_of_operation.xml',
        'data/sequence.xml',
        'data/product.xml',
        'data/mail_template.xml',
        'data/warehouse.xml',
        'views/frm_view.xml',
        'views/masters_view.xml',
        'views/stock_picking_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
