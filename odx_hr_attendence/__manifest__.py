# -*- coding: utf-8 -*-
{
    'name': "Odx Hr Attendence",

    'summary': """
        """,

    'description': """

    """,

    'author': "OdoxSofthub",
    'website': "http://www.odoxsofthub.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','om_hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
