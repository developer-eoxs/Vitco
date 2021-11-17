# -*- coding: utf-8 -*-

{
    'name': 'VRM',
    'category': 'Sale',
    'sequence': 13,
    'summary': '',
    'author': 'Odox',
    'website': 'https://www.odoxsofthub.com',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'crm', 'purchase', 'sales_team', 'mail', 'calendar',
                'resource', 'fetchmail', 'utm', 'contacts', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/vrm_lead_lost_views.xml',
        'views/vrm_views.xml',
        'views/vrm_lead_views.xml',
        'views/calendar_views.xml',
        'views/vrm_stage_views.xml',
        'views/purchase.xml',

        # 'views/vrm_team_views.xml',
        # 'views/res_partner_views.xml',
        # 'views/digest_views.xml',
        # 'views/utm_campaign_views.xml',
        # 'views/res_config_settings_views.xml',
        # 'views/vrm_menu_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
