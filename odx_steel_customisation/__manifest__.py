# -*- coding: utf-8 -*-
{
    'name': "steel customisation",

    'summary': """ """,

    'description': """  """,

    'author': "Odox",
    'website': "https://www.odoxsofthub.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','sale_management','sale_margin','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
        'views/purchase.xml',
        'views/product.xml',
        'views/sale_breakpoint.xml',
        'report/sale_history.xml',
        'report/purchase_history.xml',
    ],
    # only loaded in demonstration mode
    
}
