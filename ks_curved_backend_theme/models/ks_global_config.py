# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class KsThemeGlobalConfig(models.Model):
    _name = "ks.global.config"
    _rec_name = 'ks_recname'
    _description = "Global Settings"
    # FixMe : Change the default values

    ks_recname = fields.Char(default="Global Settings")
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    ks_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    ks_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('ks_chatter_bottom', 'Bottom'), ('ks_chatter_right', 'Right')],
                                  default='ks_chatter_bottom')
    ks_website_title = fields.Char(string="Website Backend Title", default='odoo')
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    ks_website_title_enable = fields.Boolean(string="Enable Website Backend Title")
    ks_favicon = fields.Binary(string="Favicon")
    ks_company_logo_enable = fields.Boolean(string="Enable Company Logo")
    ks_small_company_logo = fields.Binary(string="Small Logo")
    ks_company_logo = fields.Binary(string="Company Logo")
    ks_enterprise_apps = fields.Boolean(string="Hide Enterprise Apps", default=False)
    ks_odoo_referral = fields.Boolean(string="Show Odoo Referral", default=False)
    ks_theme_style = fields.Selection(string="Theme Style", selection=[('curved_theme_style', 'Curved'),
                                                                       ('boxed_theme_style', 'Boxed')],
                                      default='curved_theme_style')
    ks_colors_theme = fields.Many2one(comodel_name='ks.color.theme')
    ks_button_style = fields.Selection(string="Button style", selection=[('ks_button_style_1', 'Style 1'),
                                                                         ('ks_button_style_2', 'Style 2'),
                                                                         ('ks_button_style_3', 'Style 3'),
                                                                         ('ks_button_style_4', 'Style 4'),
                                                                         ('ks_button_style_5', 'Style 5'),
                                                                         ], default='ks_button_style_1')
    ks_body_background_type = fields.Selection(string="Body Background Image",
                                               selection=[('Image', 'Image'), ('Color', 'Color')], default='Image')
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
    ks_body_background_image = fields.Binary(string="Body background Image")
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
    ks_icon_design = fields.Char(string="Icon Design")
    ks_login_page_style = fields.Selection(string="Login Page Style", selection=[('Style1', 'Style1')])
    ks_login_background_image = fields.Binary(string="Login background Image")
    ks_login_background_image_enable = fields.Boolean(string="Enable Login Background Image", default=False)
    ks_header = fields.Boolean(string="Show Header", default=False)
    ks_footer = fields.Boolean(string="Show Footer", default=False)
    ks_login_back_image_opacity = fields.Integer(string="Login Background Image Opacity")
    ks_header_content = fields.Char(string="Header Content", default="Any Message you want to display on top.")
    ks_footer_content = fields.Char(string="Footer Content", default="Any Message you want to display on bottom.")

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

    ks_body_background = fields.Char(string="Body background")
    ks_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    ks_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    ks_app_drawer_background_opacity = fields.Float(string="App Drawer Background Opacity", default=0.5)

    ks_separator_style = fields.Selection(string="Separator style", selection=[('ks_separator_1', 'Separator 1'),
                                                                               ('ks_separator_2', 'Separator 2'),
                                                                               ('ks_separator_3', 'Separator 3'),
                                                                               ('ks_separator_4', 'Separator 4'),
                                                                               ('ks_separator_5', 'Separator 5')],
                                          default='ks_separator_1')

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

    ks_theme_color = fields.Many2one(comodel_name='ks.color.theme', string='Current color theme')

    # ---- Scope ---- #
    # FixMe: Single scope fields can be displayed as dummy for now only on  HTML

    scope_ks_auto_dark_mode = fields.Selection(
        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')], default='User')
    scope_ks_list_density = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_ks_click_edit = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='User')
    scope_ks_menu_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                         default='User')
    scope_ks_favorite_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_ks_chatter = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_ks_website_title = fields.Selection(string="Scope of Website Backend Title",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')], default='Global')
    scope_ks_favicon = fields.Selection(string="Scope of Favicon",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_ks_company_logo = fields.Selection(string="Scope of company logo",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_small_company_logo = fields.Selection(string="Scope of small company logo",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')], default='Global')
    scope_ks_enterprise_apps = fields.Selection(string="Scope of Enterprise Apps",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')
    scope_ks_odoo_referral = fields.Selection(string="Scope of Odoo referral",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')],
                                              default='User')
    scope_ks_theme_style = fields.Selection(string="Scope of Theme Style",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='User')
    scope_ks_colors_theme = fields.Selection(string="Scope of Colors Theme",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_ks_font_style = fields.Selection(string="Scope of Font Style",
                                           selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='User')
    scope_ks_button_style = fields.Selection(string="Scope of Button style",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='User')
    scope_ks_body_background = fields.Selection(string="Scope of Body background",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')

    scope_ks_app_drawer_background = fields.Selection(string="Scope of App Drawer background",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='User')

    scope_ks_separator_style = fields.Selection(string="Scope of Seperator Style",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='User')
    scope_ks_tab_style = fields.Selection(string="Scope of Tab Style",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='User')
    scope_ks_checkbox_style = fields.Selection(string="Scope of Checkbox Style",
                                               selection=[('User', 'User'), ('Company', 'Company'),
                                                          ('Global', 'Global')],
                                               default='User')
    scope_ks_popup_animation_style = fields.Selection(string="Scope of Animation Style",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='User')
    scope_ks_loaders = fields.Selection(string="Scope of Loaders",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='User')
    scope_ks_icon_design = fields.Selection(string="Scope of Icon Design",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='User')
    scope_ks_login_page_style = fields.Selection(string="Scope of Login Style",
                                                 selection=[('User', 'User'), ('Company', 'Company'),
                                                            ('Global', 'Global')],
                                                 default='User')
    scope_ks_login_background_image = fields.Selection(string="Scope of Login Background",
                                                       selection=[('User', 'User'), ('Company', 'Company'),
                                                                  ('Global', 'Global')],
                                                       default='User')
    scope_ks_header = fields.Selection(string="Scope of Header",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='User')
    scope_ks_footer = fields.Selection(string="Scope of Footer",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='User')

    scope_ks_font_size = fields.Selection(string="Scope of Font Size",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='User')
    scope_ks_radio_button_style = fields.Selection(string="Scope of Radio Button Style",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')],
                                                   default='User')

    # Note: these fields are created only for user scopes.
    scope_ks_favtbar_autohide = fields.Selection(string="Scope of Favorite bar auto hide",
                                                 selection=[('User', 'User')],
                                                 default='User')
    scope_ks_favtbar_position = fields.Selection(string="Scope of Favorite bar position",
                                                 selection=[('User', 'User')],
                                                 default='User')
    scope_ks_show_app_name = fields.Selection(string="Scope of Apps name show",
                                              selection=[('User', 'User')],
                                              default='User')
    scope_ks_user_menu_placement = fields.Selection(string="Scope of Apps menu placement",
                                                    selection=[('User', 'User')],
                                                    default='User')
    scope_ks_menubar_autohide = fields.Selection(string="Scope of Apps menubar auto hide",
                                                 selection=[('User', 'User')],
                                                 default='User')

    ks_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)

    @api.constrains('scope_ks_company_logo')
    def ks_onchange(self):
        self.scope_ks_small_company_logo = self.scope_ks_company_logo

    def ks_get_config_value(self, ks_fields):
        """
        FixMe: Handle for multiple fields
        Todo: Create same for setting values and test for all cases
        Retrieve the value for a given field.
            :param string ks_fields: The field of the parameter value to retrieve.
            :return: The value of the parameter, or ``default`` if it does not exist.
            :rtype: Dictionary or Value depending on size of ks_fields list
        """
        ks_models = {
            'User': 'res.users',
            'Company': 'res.company',
            'Global': 'ks.global.config',
        }
        ks_scopes = self.ks_get_field_scope(['scope_' + i for i in ks_fields])
        # ks_scopes = 'Company'
        if ks_scopes and len(ks_fields) == 1:
            ks_field_value = self.env(su=True)[ks_models.get(ks_scopes)].search_read([], fields=ks_fields or [],
                                                                                     limit=1)
            return ks_field_value[0].get(str(ks_fields[0]))
        return False

    def ks_get_field_scope(self, ks_fields):
        """
        Retrive the selected model/scope for the fields
            :param ks_fields: List of fields
            :return: Dictionary or Value depending on size of ks_fields list
        """
        ks_scope_values = self.env(su=True)['ks.global.config'].search_read([], fields=ks_fields or [], limit=1)
        # if ks_fields and len(ks_scope_values) > 0 and len(ks_fields) == 1:
        #     ks_scope_values = ks_scope_values[0].get(str(ks_fields[0]))
        return ks_scope_values

    @api.model
    def ks_get_config_values(self):
        """
        Function to return scope fields values.
        :return:
        """
        ks_global_config_id = self.env.ref('ks_curved_backend_theme.ks_global_config_single_rec').id
        ks_global_data = self.sudo().search([('id', '=', ks_global_config_id)], limit=1)
        values = False
        if ks_global_data:
            values = {
                # 'scope_ks_auto_dark_mode': ks_global_data.scope_ks_auto_dark_mode,
                'scope_ks_list_density': ks_global_data.scope_ks_list_density,
                'scope_ks_click_edit': ks_global_data.scope_ks_click_edit,
                'scope_ks_menu_bar': ks_global_data.scope_ks_menu_bar,
                'scope_ks_favorite_bar': ks_global_data.scope_ks_favorite_bar,
                'scope_ks_chatter': ks_global_data.scope_ks_chatter,
                'scope_ks_website_title': ks_global_data.scope_ks_website_title,
                'scope_ks_company_logo': ks_global_data.scope_ks_company_logo,
                'scope_ks_theme_style': ks_global_data.scope_ks_theme_style,
                'scope_ks_font_style': ks_global_data.scope_ks_font_style,
                'scope_ks_button_style': ks_global_data.scope_ks_button_style,
                'scope_ks_body_background': ks_global_data.scope_ks_body_background,
                'scope_ks_separator_style': ks_global_data.scope_ks_separator_style,
                'scope_ks_tab_style': ks_global_data.scope_ks_tab_style,
                'scope_ks_checkbox_style': ks_global_data.scope_ks_checkbox_style,
                'scope_ks_popup_animation_style': ks_global_data.scope_ks_popup_animation_style,
                'scope_ks_loaders': ks_global_data.scope_ks_loaders,
                'scope_ks_font_size': ks_global_data.scope_ks_font_size,
                'scope_ks_radio_button_style': ks_global_data.scope_ks_radio_button_style,
                'scope_ks_app_drawer_background': ks_global_data.scope_ks_app_drawer_background,
                'scope_ks_colors_theme': ks_global_data.scope_ks_colors_theme,
            }
        return values

    @api.model
    def ks_save_apply_scope(self, unsaved_data):
        """
        Function to save changed scope for settings.
        :return:
        """
        ks_global_config_id = self.env.ref('ks_curved_backend_theme.ks_global_config_single_rec').id
        ks_global_data = self.sudo().search([('id', '=', ks_global_config_id)], limit=1)
        if ks_global_data:
            ks_global_data.write(unsaved_data)
            _logger.info(_("Theme setting scope is changed successfully."))

    @api.model
    def ks_get_global_setting(self):
        """
        Function to return list of dictionary for global theme setting data.
        :return:
        """
        ks_global_config_id = self.env.ref('ks_curved_backend_theme.ks_global_config_single_rec').id
        ks_global_data = self.sudo().search([('id', '=', ks_global_config_id)], limit=1)
        values = {
            'ks_menu_bar': ks_global_data.ks_menu_bar,
            'ks_theme_style': ks_global_data.ks_theme_style,
            'ks_font_style': ks_global_data.ks_font_style,
            'ks_font_size': ks_global_data.ks_font_size,
            'ks_button_style': ks_global_data.ks_button_style,
            'ks_body_background': ks_global_data.ks_body_background,
            'ks_separator_style': ks_global_data.ks_separator_style,
            'ks_tab_style': ks_global_data.ks_tab_style,
            'ks_checkbox_style': ks_global_data.ks_checkbox_style,
            'ks_radio_button_style': ks_global_data.ks_radio_button_style,
            'ks_popup_animation_style': ks_global_data.ks_popup_animation_style,
            'ks_loaders': ks_global_data.ks_loaders,
        }
        return values

    @api.model
    def get_body_background(self, ks_fields):
        """
        function to return body background and opacity based on its scope and currently active background.
        :return:
        """
        ks_global_config_id = self.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
        ks_image_model = {
            'ks_body_background': 'ks.body.background',
            'ks_app_drawer_background': 'ks.drawer.background'
        }
        ks_result = {}

        for rec in ks_fields:
            # First check for scope
            scope = ks_global_config_id.sudo()['scope_' + rec]
            ks_origin_data = False
            if scope == 'Global':
                ks_origin_data = ks_global_config_id
                ks_domain = [('ks_global', '=', True), ('ks_active', '=', True)]

            if scope == 'Company':
                ks_origin_data = self.env.user.company_id
                ks_domain = [('ks_company', '=', ks_origin_data.id), ('ks_active', '=', True)]

            if scope == 'User':
                ks_origin_data = self.env.user
                ks_domain = [('ks_user', '=', ks_origin_data.id), ('ks_active', '=', True)]

            if not ks_origin_data:
                return False

            if ks_origin_data[rec]:
                ks_result[rec] = {
                    'type': 'color',
                    'value': ks_origin_data[rec][:ks_origin_data[rec].rfind(',')] + ', ' + str(
                        ks_origin_data[rec + '_opacity']) + ')',
                }
                if rec == 'ks_app_drawer_background':
                    ks_drawer_font_style = self.env['ks.drawer.colors'].sudo().search(
                        [('ks_colors', '=', ks_origin_data[rec])])
                    if ks_drawer_font_style:
                        ks_result['ks_drawer_font_style'] = ks_drawer_font_style.ks_font_style
            if not ks_origin_data[rec]:
                ks_back = self.env[ks_image_model[rec]].sudo().search(ks_domain, limit=1)
                ks_result[rec] = {
                    'type': 'image',
                    'value': self.ks_get_image_url(ks_back.ks_image),
                    'opacity': ks_origin_data[rec + '_opacity']
                }
                if rec == 'ks_body_background':
                    ks_body_background_image_enable = True
                    if scope == 'User':
                        ks_body_background_image_enable = self.sudo().env.user.ks_body_background_image_enable
                    if scope == 'Company':
                        ks_body_background_image_enable = self.sudo().env.user.company_id.ks_body_background_image_enable
                    if scope == 'Global':
                        ks_body_background_image_enable = ks_global_config_id.ks_body_background_image_enable

                    if not ks_body_background_image_enable:
                        ks_result[rec]['value'] = False

        return ks_result

    @api.model
    def ks_get_image_url(self, data):
        file_type_magic_word = {
            '/': 'jpg',
            'R': 'gif',
            'i': 'png',
            'P': 'svg+xml',
        }
        if not data:
            return False
        return 'data:image/' + (file_type_magic_word.get(data[0]) or 'png') + ';base64,' + data.decode("utf-8")

    @api.model
    def ks_get_value_from_scope(self, ks_field_list):
        ks_global_origin = self.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
        ks_user = self.env.user
        ks_company = self.env.user.company_id
        ks_result = {}

        # Get fields scope
        ks_scopes = ks_global_origin.ks_get_field_scope(['scope_' + i for i in ks_field_list])

        # compute fields value based on the scope.
        if len(ks_scopes):
            for key, value in ks_scopes[0].items():
                if value == 'User':
                    self.ks_get_field_value(ks_user, key.split('scope_')[1], ks_result)
                if value == 'Company':
                    self.ks_get_field_value(ks_company, key.split('scope_')[1], ks_result)
                if value == 'Global':
                    self.ks_get_field_value(ks_global_origin, key.split('scope_')[1], ks_result)
        return ks_result

    def ks_get_field_value(self, origin_data, key, ks_result):
        # check for special fields
        ks_special_fields = self.ks_get_special_fields()
        if key in ks_special_fields.keys():
            # special fields will check it will only returns the data if its enabler field is checked.
            if origin_data[ks_special_fields[key]]:
                ks_result[key] = origin_data[key]
            else:
                ks_result[key] = False
        else:
            ks_result[key] = origin_data[key]

    def ks_get_special_fields(self):
        return {'ks_company_logo': 'ks_company_logo_enable',
                'ks_small_company_logo': 'ks_company_logo_enable'}
