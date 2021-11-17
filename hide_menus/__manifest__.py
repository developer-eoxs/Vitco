# -*- coding: utf-8 -*-
{
    'name': "hide_menus",

    'summary': """
        Hide Menus and Configurations Menus 
        """,

    'description': """
        Hide Menus and Configurations Menus 
        for Users and give access to Administration/setting
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '13.0',

    # any module necessary for this one to work correctly
    'depends': ['base',
        'utm',
        'link_tracker',
        'website_slides',
        'repair',
        'project',
        'mass_mailing',
        'crm',
        'contacts',
        'sale',
        'odx_vrm',
        'hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/modules_menu.xml',
        'security/config_menu.xml',
        'views/configuration_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
