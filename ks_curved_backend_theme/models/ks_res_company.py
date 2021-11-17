from odoo import models, fields


class KsResCompany(models.Model):
    _inherit = 'res.company'
    # ToDo: Add Default Values and strings

    ks_website_title = fields.Char(string="Website Backend Title", default='odoo')
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    ks_website_title_enable = fields.Boolean(string="Enable Website Backend Title")
    ks_favicon = fields.Binary(string="Favicon")
    ks_company_logo_enable = fields.Boolean(string="Enable Company Logo")
    ks_company_logo = fields.Binary(string="Main Company Logo")
    ks_small_company_logo = fields.Binary(string="Small Logo")
    ks_header = fields.Boolean(string="Show Header", default=False)
    ks_footer = fields.Boolean(string="Show Footer", default=False)
    ks_header_content = fields.Char(string="Header Content", default="Any Message you want to display on top.")
    ks_footer_content = fields.Char(string="Footer Content", default="Any Message you want to display on bottom.")
    ks_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    ks_theme_style = fields.Selection(string="Theme Style", selection=[('curved_theme_style', 'Curved'),
                                                                       ('boxed_theme_style', 'Boxed')],
                                      default='curved_theme_style')
    ks_font_style = fields.Selection(string="Font Style", selection=[('ks_font_poppins', 'Poppins'),
                                                                     ('ks_font_lato', 'Lato'),
                                                                     ('ks_font_raleway', 'Raleway'),
                                                                     ('ks_font_arial', 'Arial'),
                                                                     ('ks_font_times_new', 'Times new'),
                                                                     ('ks_font_open_san', 'Open San'),
                                                                     ('ks_font_roboto', 'Roboto'),
                                                                     ('ks_font_ubuntu', 'Ubuntu'),
                                                                     ])

    ks_font_size = fields.Selection(string="Font Size", selection=[('ks_font_size_small', 'Small'),
                                                                   ('ks_font_size_medium', 'Medium'),
                                                                   ('ks_font_size_large', 'Larger'),
                                                                   ('ks_font_size_extra_large', 'Extra Large')
                                                                   ], default='ks_font_size_medium')

    ks_button_style = fields.Selection(string="Button style", selection=[('ks_button_style_1', 'Style 1'),
                                                                         ('ks_button_style_2', 'Style 2'),
                                                                         ('ks_button_style_3', 'Style 3'),
                                                                         ('ks_button_style_4', 'Style 4'),
                                                                         ('ks_button_style_5', 'Style 5'),
                                                                         ], default='ks_button_style_1')

    ks_separator_style = fields.Selection(string="Separator style", selection=[('ks_separator_1', 'Separator 1'),
                                                                               ('ks_separator_2', 'Separator 2'),
                                                                               ('ks_separator_3', 'Separator 3'),
                                                                               ('ks_separator_4', 'Separator 4'),
                                                                               ('ks_separator_5', 'Separator 5')],
                                          default='ks_separator_1')

    ks_tab_style = fields.Selection(string="Tab style", selection=[('ks_tab_style1', 'Style 1'),
                                                                   ('ks_tab_style2', 'Style 2'),
                                                                   ('ks_tab_style3', 'Style 3'),
                                                                   ('ks_tab_style4', 'Style 4'),
                                                                   ('ks_tab_style5', 'Style 5'),
                                                                   ], default='ks_tab_style1')

    ks_checkbox_style = fields.Selection(string="Checkbox style",
                                         selection=[('ks_checkbox_1', 'Style 1'), ('ks_checkbox_2', 'Style 2'),
                                                    ('ks_checkbox_3', 'Style 3'),
                                                    ('ks_checkbox_4', 'Style 4'), ('ks_checkbox_5', 'Style 5')],
                                         default='ks_checkbox_1')

    ks_radio_button_style = fields.Selection(string="Radio Button Style",
                                             selection=[('ks_radio_button_1', 'Style 1'),
                                                        ('ks_radio_button_2', 'Style 2'),
                                                        ('ks_radio_button_3', 'Style 3'),
                                                        ('ks_radio_button_4', 'Style 4'),
                                                        ('ks_radio_button_5', 'Style 5')], default='ks_radio_button_1')

    ks_popup_animation_style = fields.Selection(string="Popup Animation style",
                                                selection=[('ks_popup_style1', 'Style 1'),
                                                           ('ks_popup_style2', 'Style 2'),
                                                           ('ks_popup_style3', 'Style 3'),
                                                           ('ks_popup_style4', 'Style 4'),
                                                           ('ks_popup_style5', 'Style 5'),
                                                           ('ks_popup_style6', 'Style 6'),
                                                           ('ks_popup_style7', 'Style 7'),
                                                           ('ks_popup_style8', 'Style 8'),
                                                           ('ks_popup_style9', 'Style 9'),
                                                           ('ks_popup_style10', 'Style 10'),
                                                           ], default='ks_popup_style1')

    ks_loaders = fields.Selection(string="Loading Bar", selection=[('ks_loader_1', 'Loader 1'),
                                                                   ('ks_loader_2', 'Loader 2'),
                                                                   ('ks_loader_3', 'Loader 3'),
                                                                   ('ks_loader_4', 'Loader 4'),
                                                                   ('ks_loader_5', 'Loader 5'),
                                                                   ], default='ks_loader_1')


    ks_body_background = fields.Char(string="Body background", default=False)
    ks_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    ks_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    ks_app_drawer_background_opacity = fields.Float(string="App Drawer background Opacity", default=0.5)

    ks_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('ks_chatter_bottom', 'Bottom'), ('ks_chatter_right', 'Right')],
                                  default='ks_chatter_bottom')

    ks_theme_color = fields.Many2one(comodel_name='ks.color.theme', string='Current color theme')

    ks_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)
