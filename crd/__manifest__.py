# -*- coding: utf-8 -*-
{
    'name': "Customer Relation",
    'summary': """
        Customer Relation
        """,
    'description': """
        Customer Relation
    """,
    'author': "OdoxSofthub",
    'website': "http://www.odoxsofthub.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale', 'stock', 'odx_product_custom_steel', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/crd_line_view.xml',
        'views/crd_view.xml',
        'views/customer_requirements.xml',
        # 'views/sale_order.xml',
        'wizard/product_wizard_view.xml',
        'wizard/crd_import_wizard.xml',
    ],
    'demo': [
    ],
}
