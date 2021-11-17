from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class KsResUsers(models.Model):
    _inherit = 'res.users'

    ks_frequency_menu = fields.One2many(string="Frequency Menu", inverse_name='ks_user_id',
                                        comodel_name="ks.frequency.counter",
                                        help="To count frequency")
    ks_ir_ui_view = fields.Many2one(string="View", comodel_name="ir.ui.view")
    ks_favt_app_ids = fields.Many2many(string="Favorite Apps", comodel_name="ir.ui.menu",
                                       relation="ks_users_favt_ir_menu",
                                       column1="ks_user", column2="ks_favt_menu",
                                       help="To store all user favorite apps")
    ks_bookmark_ids = fields.One2many(string="Bookmarks", comodel_name="ks.bookmark", inverse_name="ks_user_id",
                                      help="To acess bookmark")
    # ---------- Theme Config Fields 👇 ---------- #
    ks_dark_mode = fields.Boolean(string="Dark Mode", default=False)
    ks_auto_dark_mode = fields.Boolean(string="Auto-Dark Mode", default=False)
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    ks_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    ks_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('ks_chatter_bottom', 'Bottom'), ('ks_chatter_right', 'Right')],
                                  default='ks_chatter_bottom')
    ks_favorite_bar = fields.Boolean(string="Show Favorite Apps", default=True)
    ks_favtbar_autohide = fields.Boolean(string="Auto-hide Favorite Bar", default=False)
    ks_menubar_autohide = fields.Boolean(string="Auto-hide Menu Bar", default=False)
    ks_favtbar_position = fields.Selection(string="Favoritebar Position",
                                           selection=[('Bottom', 'Bottom'), ('Left', 'Left')], default='Left')
    ks_list_density = fields.Selection(string="List View Style",
                                       selection=[('Default', 'Default'), ('Comfortable', 'Comfortable'),
                                                  ('Attachment', 'Attachment')],
                                       default='Default')
    ks_show_app_name = fields.Boolean(string="Display App Names", default=True)
    ks_user_menu_placement = fields.Selection(string="User Menu Placement",
                                              selection=[('Bottom', 'Bottom'), ('Top', 'Top')], default='Bottom')
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

    ks_button_style = fields.Selection(string="Button style", selection=[('ks_button_style_1', 'Style 1'),
                                                                         ('ks_button_style_2', 'Style 2'),
                                                                         ('ks_button_style_3', 'Style 3'),
                                                                         ('ks_button_style_4', 'Style 4'),
                                                                         ('ks_button_style_5', 'Style 5'),
                                                                         ], default='ks_button_style_1')

    ks_loaders = fields.Selection(string="Loading Bar", selection=[('ks_loader_1', 'Loader 1'),
                                                                   ('ks_loader_2', 'Loader 2'),
                                                                   ('ks_loader_3', 'Loader 3'),
                                                                   ('ks_loader_4', 'Loader 4'),
                                                                   ('ks_loader_5', 'Loader 5'),
                                                                   ], default='ks_loader_1')

    ks_separator_style = fields.Selection(string="Separator style", selection=[('ks_separator_1', 'Separator 1'),
                                                                               ('ks_separator_2', 'Separator 2'),
                                                                               ('ks_separator_3', 'Separator 3'),
                                                                               ('ks_separator_4', 'Separator 4'),
                                                                               ('ks_separator_5', 'Separator 5')],
                                          default='ks_separator_1')

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

    ks_tab_style = fields.Selection(string="Tab style", selection=[('ks_tab_style1', 'Style 1'),
                                                                   ('ks_tab_style2', 'Style 2'),
                                                                   ('ks_tab_style3', 'Style 3'),
                                                                   ('ks_tab_style4', 'Style 4'),
                                                                   ('ks_tab_style5', 'Style 5'),
                                                                   ], default='ks_tab_style1')

    ks_body_background = fields.Char(string="Body background", default=False)
    ks_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    ks_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    ks_app_drawer_background_opacity = fields.Float(string="App Drawer background Opacity", default=0.5)

    ks_body_background_color = fields.Selection(selection=[('body_back_color_1', 'Body Background Color 1'),
                                                           ('body_back_color_2', 'Body Background Color 2'),
                                                           ('body_back_color_3', 'Body Background Color 3'),
                                                           ('body_back_color_4', 'Body Background Color 4'),
                                                           ('body_back_color_5', 'Body Background Color 5'),
                                                           ('body_back_color_6', 'Body Background Color 6'),
                                                           ('body_back_color_7', 'Body Background Color 7'),
                                                           ('body_back_color_8', 'Body Background Color 8')],
                                                default='body_back_color_1',
                                                string="Body Background Color")

    ks_sunrise_hour = fields.Integer(string="Sunrise Time", help="Sunrise time HH:MM format")
    ks_sunrise_min = fields.Integer()
    ks_sunset_hour = fields.Integer(string="Sunset Time", help="Sunset time HH:MM format")
    ks_sunset_min = fields.Integer()

    ks_theme_color = fields.Many2one(comodel_name='ks.color.theme', string='Current color theme')
    ks_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)

    def __init__(self, pool, cr):
        init_res = super().__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = self.SELF_WRITEABLE_FIELDS + ['ks_sunrise_hour', 'ks_sunrise_min',
                                                                         'ks_sunset_hour', 'ks_sunset_min']
        return init_res

    @api.constrains('ks_sunrise_hour', 'ks_sunrise_min', 'ks_sunset_hour', 'ks_sunset_min')
    def ks_check_suntime(self):
        if self.ks_sunrise_hour > self.ks_sunset_hour or (
                self.ks_sunrise_hour == self.ks_sunset_hour and self.ks_sunrise_min > self.ks_sunset_min):
            raise ValidationError(_("sunrise happens before sunset."))
        if self.ks_sunrise_hour < 0 or self.ks_sunset_hour < 0 or self.ks_sunrise_min < 0 or self.ks_sunset_min < 0:
            raise ValidationError(_("Time can't be negative."))
        if self.ks_sunrise_hour > 23 or self.ks_sunset_hour > 23 or self.ks_sunrise_min > 59 or self.ks_sunset_min > 59:
            raise ValidationError(_("Please enter values in correct time."))
