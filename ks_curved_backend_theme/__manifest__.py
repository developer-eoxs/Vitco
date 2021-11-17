# -*- coding: utf-8 -*-
{
    'name': "Arc Backend Theme",
    'summary': """
        The most prolific Odoo backend themes 
        - Arc! With some of the best features like the dark theme, app drawer background, radio button style customizations, and much more, backgrounds are going to be more appealing than ever!
    """,
    'description': """
        odoo backend themes
        odoo responsive backend theme
        odoo themes
        odoo backend theme V13
        odoo 13 backend theme
        backend theme odoo
        odoo enterprise theme
        odoo custom themes
        odoo theme download
        change odoo backend theme
        odoo material backend theme
        odoo theme backend
        backend theme odoo apps
        odoo backend theme customize
        change backend theme odoo
        odoo backend layout theme
        customizable odoo Theme
        customize odoo backend
        change odoo backend color
        odoo app backend theme
        Arc Theme
	    Arc Themes
	    Backend Theme
        Backend Themes
        Curved Theme
	    Boxed Theme
    	Curved Backend Theme
	    Odoo Arc Theme
	    Odoo Arc Backend Theme
	    Odoo Arc
	    Odoo Backend Theme
	    Ksolves Arc
	    Ksolves Arc Theme
	    Ksolves Arc Backend Theme
	    Ksolves Odoo Theme
	    Ksolves Odoo Backend Theme
	    Ksolves Backend Theme
	    Ksolves Themes
    """,
    'author': "Ksolves India Ltd.",
    'website': "https://www.ksolves.com",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': '149.0',
    'version': '13.0.1.0.0',
    'live_test_url': 'https://arctheme13.kappso.com/web/demo_login',
    'category': 'Themes/Backend',
    'support': 'sales@ksolves.com',
    'depends': ['web'],

    # always loaded
    'data': [
        'data/data.xml',
        'data/ks_drawer_colors.xml',
        'data/ks_color_theme.xml',
        'security/ir.model.access.csv',
        'security/curved_theme_security.xml',
        'views/views.xml',
        'views/ks_main_panel.xml',
        'views/templates.xml',
        'views/ks_assets.xml',
        'views/ks_assets_popup_animation.xml',
        'views/ks_login_page.xml',
        'views/ks_res_users_preferences.xml',
    ],

    'qweb': [
        'static/src/xml/ks_menu.xml',
        'static/src/xml/ks_left_sidebar_panel.xml',
        'static/src/xml/ks_switch_language.xml',
        'static/src/xml/ks_quick_settings.xml',
        'static/src/xml/ks_global_settings.xml',
        'static/src/xml/ks_fullscreen.xml',
        'static/src/xml/ks_search_panel.xml',
        'static/src/xml/ks_company_settings.xml',
        'static/src/xml/ks_bookmark.xml',
        'static/src/xml/ks_appdrawer_edit.xml',
        'static/src/xml/ks_calendar_view.xml',
    ],
    'images': [
        'static/description/Banner.jpg',
        'static/description/list_screenshot.gif',
    ],

    "application": True,
    "installable": True,
}
