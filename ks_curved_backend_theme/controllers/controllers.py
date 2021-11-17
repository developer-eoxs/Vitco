# -*- coding: utf-8 -*-
from odoo.http import request, route, _logger
import requests
from datetime import datetime
import base64
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

from odoo import http, _


class KsCurvedBackendTheme(http.Controller):

    @route(['/update/bookmarks'], type='json', auth='user')
    def update_bookmarks(self, **post):
        """
        Update the Bookmarks
        :param post: dict of functionality(create_new, rename, reposition, delete) and corresponding bookmark details
        :return: Updated XML template of bookmark
        """
        user_id = request.env.user.id
        if post.get('create_new', False):
            bookmark_name = post['bookmark_name']
            bookmark_url = post['bookmark_url']
            bookmark_position = post['bookmark_position']
            request._cr.execute(
                'insert into ks_bookmark (ks_bookmark_name,ks_bookmark_url,ks_bookmark_position,ks_user_id) values (%s,%s,%s,%s)',
                (bookmark_name, bookmark_url, bookmark_position, user_id))
        elif post.get('rename', False):
            bookmark_name = post['bookmark_name']
            bookmark_id = post['bookmark_id']
            request._cr.execute('update ks_bookmark set ks_bookmark_name=%s where id = %s and ks_user_id = %s ',
                                (bookmark_name, bookmark_id, user_id))
        elif post.get('reposition', False):
            bookmark_id = post['bookmark_id']
            bookmark_position = int(post['bookmark_position'])
            reposition = post['reposition']
            new_position = False
            if reposition == 'move_up':
                new_position = bookmark_position - 1
            elif reposition == 'move_down':
                new_position = bookmark_position + 1
            else:
                _logger.info("Unable to change position of Bookmark.")
            if new_position:
                request._cr.execute('update ks_bookmark set ks_bookmark_position=%s where id = %s and ks_user_id = %s ',
                                    (new_position, bookmark_id, user_id))
                request._cr.execute(
                    'update ks_bookmark set ks_bookmark_position=%s where ks_bookmark_position = %s and ks_user_id = %s and id!=%s ',
                    (bookmark_position, new_position, user_id, bookmark_id))
        elif post.get('delete', False):
            bookmark_id = post['bookmark_id']
            request._cr.execute('Delete from ks_bookmark where id =%s and ks_user_id = %s',
                                (bookmark_id, user_id))
        ks_bookmarks = request.env['ks.bookmark'].search([('ks_user_id', '=', user_id)], order='ks_bookmark_position')
        values = {
            'bookmarks': ks_bookmarks,
        }
        return request.env['ir.ui.view'].render_template("ks_curved_backend_theme.ks_bookmark_", values)

    @route(['/render/bookmarks'], type='json', auth='user')
    def render_bookmark_template(self):
        """
        Render the HTML of User's bookmarks
        :return: XML Template of Bookmark
        """
        user_id = request.env.user.id
        ks_bookmarks = request.env['ks.bookmark'].search([('ks_user_id', '=', user_id)], order='ks_bookmark_position')
        values = {
            'bookmarks': ks_bookmarks,
        }
        return request.env['ir.ui.view'].render_template("ks_curved_backend_theme.ks_bookmark_", values)

    @route(['/get/installed/languages'], type='json', auth='public')
    def get_languages(self):
        """
        Render the list of installed languages
        :return: list of tuples of short code & languages
        """
        languages = request.env['res.lang'].get_installed()
        return languages

    @route(['/selected/language'], type='json', auth='public')
    def user_selected_language(self, selected_language):
        """
        To switch the user language
        :param selected_language: string of language short code
        """
        request.env.user.lang = selected_language

    @route(['/render/theme/view/data'], type='json', auth='user')
    def render_theme_view_settings(self, ks_setting_scope, ks_rec_id=None):
        """
        Function to return theme setting data for company/global to visible current company/global setting on the form
        view.
        :param ks_setting_scope:
        :return:
        """
        ks_origin_data = False
        ks_domain = []
        values = {}
        ks_all_setting_scope = request.env['ks.global.config'].ks_get_config_values()
        if ks_setting_scope == 'User':
            user = request.env.user
            values = self.ks_get_values(ks_all_setting_scope, user, ks_setting_scope)
            ks_domain = [('ks_user', '=', user.id)]

            ks_color_theme = False
            if ks_all_setting_scope['scope_ks_colors_theme'] == 'User':
                ks_color_theme = request.env(su=True)['ks.color.theme'].get_theme(scope=ks_setting_scope, origin=user)
            values.update({
                'ks_sun_time_info': self.ks_get_suntime_info(),
                'ks_dark_mode': user.ks_dark_mode,
                'ks_auto_dark_mode': self.ks_get_dark_mode(),
                'ks_menubar_autohide': user.ks_menubar_autohide,
                'ks_favtbar_autohide': user.ks_favtbar_autohide,
                'ks_favtbar_position': user.ks_favtbar_position,
                'ks_show_app_name': user.ks_show_app_name,
                'ks_user_menu_placement': user.ks_user_menu_placement,
                'ks_manager_role': user.has_group('ks_curved_backend_theme.ks_curved_theme_settings'),
                'ks_global_config_id': request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec').id,
                'ks_body_background_img': self.ks_get_background_data(ks_domain, 'ks.body.background'),
                'ks_app_drawer_background_img': self.ks_get_background_data(ks_domain, 'ks.drawer.background'),
                'ks_body_background_opacity': user.ks_body_background_opacity,
                'ks_app_drawer_background_opacity': user.ks_app_drawer_background_opacity,
                'ks_body_background_image_enable': user.ks_body_background_image_enable,
                'ks_color_theme': ks_color_theme,
            })

            # Update currently active menu bar
            ks_current_menu_bar_scope = ks_all_setting_scope['scope_ks_menu_bar']
            if ks_current_menu_bar_scope == 'Global':
                ks_origin_data = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
                ks_new_values = self.ks_get_values({'scope_ks_menu_bar': ks_current_menu_bar_scope}, ks_origin_data,
                                                   ks_current_menu_bar_scope)
                values.update({'ks_current_menu_bar': ks_new_values.get('ks_menu_bar')})
            elif ks_current_menu_bar_scope == 'Company':
                ks_origin_data = request.env.user.company_id
                ks_new_values = self.ks_get_values({'scope_ks_menu_bar': ks_current_menu_bar_scope}, ks_origin_data,
                                                   ks_current_menu_bar_scope)
                values.update({'ks_current_menu_bar': ks_new_values.get('ks_menu_bar')})
            elif ks_current_menu_bar_scope == 'User':
                values.update({'ks_current_menu_bar': values.get('ks_menu_bar')})

        if ks_setting_scope == 'Company':
            ks_origin_data = request.env['res.company'].browse(ks_rec_id)
            ks_domain = [('ks_company', '=', ks_origin_data.id)]
            values = self.ks_get_values(ks_all_setting_scope, ks_origin_data, ks_setting_scope)
        if ks_setting_scope == 'Global':
            ks_origin_data = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
            ks_domain = [('ks_global', '=', True)]
            values = self.ks_get_values(ks_all_setting_scope, ks_origin_data, ks_setting_scope)
        # Only for company and global since user have different value of dictionary.
        # User needs to have different dictionary since it needs to manage hide and show tabs for settings based on
        # the scope.
        if ks_setting_scope in ['Company', 'Global']:
            ks_color_theme = False
            if (ks_all_setting_scope['scope_ks_colors_theme'] == 'Company' and ks_setting_scope == 'Company') or (
                    ks_setting_scope == 'Global'):
                ks_color_theme = request.env(su=True)['ks.color.theme'].get_theme(scope=ks_setting_scope,
                                                                                  origin=ks_origin_data)
            values.update({
                'ks_body_background_opacity': ks_origin_data.ks_body_background_opacity,
                'ks_app_drawer_background_opacity': ks_origin_data.ks_app_drawer_background_opacity,
                'ks_website_title_enable': ks_origin_data.ks_website_title_enable,
                'ks_company_logo_enable': ks_origin_data.ks_company_logo_enable,
                'ks_small_company_logo': self.ks_get_image_url(ks_origin_data.ks_small_company_logo),
                'ks_body_background_img': self.ks_get_background_data(ks_domain, 'ks.body.background'),
                'ks_app_drawer_background_img': self.ks_get_background_data(ks_domain, 'ks.drawer.background'),
                'ks_color_theme': ks_color_theme,
                'ks_body_background_image_enable': ks_origin_data.ks_body_background_image_enable,
            })
            if 'ks_company_logo' in values:
                values.update({
                    'ks_company_logo': self.ks_get_image_url(ks_origin_data.ks_company_logo)
                })

        if ks_setting_scope == 'Global':
            values['ks_enterprise_apps'] = ks_origin_data.ks_enterprise_apps
            values['ks_login_background_image_enable'] = ks_origin_data.ks_login_background_image_enable
            values['ks_login_background_image'] = self.ks_get_image_url(ks_origin_data.ks_login_background_image)
            values['ks_color_theme_scope'] = ks_all_setting_scope['scope_ks_colors_theme']
        return values

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

    def ks_get_values(self, ks_all_setting_scope, ks_origin, ks_current_scope):
        """
        Function to get values to render on the page.
        :param ks_all_setting_scope: all setting scopes.
        :param ks_origin: origin of the data.
        :param ks_current_scope: current scope.
        :return: values to render on the page.
        """
        values = dict()
        for key, value in ks_all_setting_scope.items():
            if value == ks_current_scope and key.split('scope_')[1] in ks_origin:
                values[key.split('scope_')[1]] = ks_origin[key.split('scope_')[1]] if ks_origin[
                    key.split('scope_')[1]] else True

                # Handle boolean field
                if key == 'scope_ks_favorite_bar':
                    values[key.split('scope_')[1]] = ks_origin[key.split('scope_')[1]]
                if key == 'scope_ks_click_edit':
                    values[key.split('scope_')[1]] = ks_origin[key.split('scope_')[1]]
        return values

    def ks_get_background_data(self, ks_domain, ks_model):
        """
        Function to return the body background data based on the scope for global, companies, and users.
        :param ks_domain:
        :return:
        """
        ks_body_background_img = []
        for ks_background in request.env[ks_model].search(
                ks_domain):
            ks_body_background_img.append({
                'id': str(ks_background.id),
                'ks_active': ks_background.ks_active,
                'value': self.ks_get_image_url(ks_background.ks_image)
            })
        return ks_body_background_img

    @route(['/save/theme/settings'], type='json', auth='user')
    def save_theme_settings(self, **post):
        """
        Save the settings of Theme
        :param post: dict of field and its value
        """

        # ks_no_check_field have special functionality to write/create data in other models.
        ks_no_check_field = ['ks_body_background_img', 'ks_app_drawer_background_img']
        ks_theme_fields = ["ks_body_background",
                           "ks_menu",
                           "ks_menu_hover",
                           "ks_button",
                           "ks_border",
                           "ks_heading",
                           "ks_link",
                           "ks_primary_color",
                           "ks_tooltip"]
        ks_image_model = {
            'ks_body_background_img': 'ks.body.background',
            'ks_app_drawer_background_img': 'ks.drawer.background'
        }
        ks_background_data = {}
        ks_background_domain = []
        ks_splitter = ''

        ks_origin_obj = False
        if post.get('ks_origin_scope') == 'user':
            # if setting is changed then active and de-active the templates.
            ks_origin_obj = request.env.user
            ks_background_data['ks_user'] = ks_origin_obj.id
            ks_background_domain = [('ks_user', '=', ks_origin_obj.id)]
            ks_color_theme_domain = [('ks_user', '=', ks_origin_obj.id), ('ks_active', '=', True)]

        if post.get('ks_origin_scope') == 'company':
            ks_origin_obj = request.env['res.company'].browse(post['record_id'])
            ks_splitter = '_company'
            ks_background_data['ks_company'] = ks_origin_obj.id
            ks_background_domain = [('ks_company', '=', ks_origin_obj.id)]
            ks_color_theme_domain = [('ks_company', '=', ks_origin_obj.id), ('ks_active', '=', True)]

        if post.get('ks_origin_scope') == 'global':
            ks_origin_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
            ks_splitter = '_global'
            ks_background_data['ks_global'] = True
            ks_background_domain = [('ks_global', '=', True)]
            ks_color_theme_domain = [('ks_global', '=', True), ('ks_active', '=', True)]

        for key, value in post.get('ks_unsaved_setting').items():
            # check for special field data need to update or create new data on its model.
            if key in ks_no_check_field:
                if type(value) is int:
                    # Need to de-active other background and active selected image.
                    for ks_background in request.env[ks_image_model[key]].search(ks_background_domain):
                        if ks_background.id == value:
                            ks_background.write({'ks_active': True})
                        else:
                            ks_background.write({'ks_active': False})
                else:
                    ks_background_data['ks_image'] = value
                    request.env[ks_image_model[key]].create(ks_background_data)
            elif ks_splitter and ks_splitter in key:
                if key.rsplit(ks_splitter, 1)[0] not in ks_theme_fields:
                    ks_origin_obj[key.rsplit(ks_splitter, 1)[0]] = value
            else:
                ks_origin_obj[key] = value

            # Manage theme colors active.
            if key == 'ks_theme_color':
                # de-active current theme
                ks_current_theme = request.env['ks.color.theme'].sudo().search(ks_color_theme_domain)
                for rec in ks_current_theme:
                    rec.write({'ks_active': False})
                # active new theme
                ks_new_theme = request.env['ks.color.theme'].sudo().search([('id', '=', value)], limit=1)
                if ks_new_theme:
                    ks_new_theme.write({'ks_active': True})

        # Hide or show enterprise apps.
        if 'ks_enterprise_apps' in post['ks_unsaved_setting']:
            request.env.ref('ks_curved_backend_theme.ks_curved_theme_hide_enterprise_apps').write({
                'active': post['ks_unsaved_setting'].get('ks_enterprise_apps')
            })

    @route(['/ks_list_renderer/attachments'], type='json', auth='user')
    def ks_list_render(self, **kw):
        """
        Fetches the details of attachments of all renderd records in List View.
        :param kw: {res_ids, model}
        :return: values {rec_id:[{att_id, att_name, att_mime}]}
        """
        tree_view_ids = kw.get('res_ids')
        tree_view_model = kw.get('model')

        # Handle do action from js
        tree_view_domain = kw.get('domain')
        ks_domain = []
        for view_domain in tree_view_domain:
            if type(view_domain) is list:
                ks_domain.append(tuple(view_domain))
            else:
                ks_domain.append(view_domain)
        if not tree_view_ids:
            tree_view_ids = request.env[tree_view_model].sudo().search(ks_domain).ids

        values = {}
        for tree_view_rec_id in tree_view_ids:
            attachment_ids = False
            # Check if tree_view_rec_id is integer.
            if type(tree_view_rec_id) is int:
                attachment_ids = request.env['ir.attachment'].search(
                    [('res_model', '=', tree_view_model), ('res_id', '=', tree_view_rec_id)]).ids
            if attachment_ids:
                values.update({tree_view_rec_id: ''})
                for attachment_id in attachment_ids:
                    data = request.env['ir.attachment'].browse(attachment_id)
                    if data:
                        if len(values.get(tree_view_rec_id)):
                            values[tree_view_rec_id].append({
                                'att_id': data.id,
                                'att_name': data.display_name,
                                'att_mime': data.mimetype
                            })
                        else:
                            values[tree_view_rec_id] = [{
                                'att_id': data.id,
                                'att_name': data.display_name,
                                'att_mime': data.mimetype
                            }]
        data = [values]
        list_density = {'ks_list_density': request.env.user.ks_list_density}
        data.append(list_density)

        # Append checkbox style for tree view.
        data.append({'ks_checkbox_style': self.ks_get_checkbox_style()})
        return data

    @route(['/ks_app_frequency/update'], type='json', auth='user')
    def ks_app_frequency_update(self, **kw):
        """
        To update the frequency of apps as per users
        :param kw: dict containing Primary Menu id
        """
        menu_id = kw['menu_id']
        user_id = request.env.user
        if menu_id in user_id.ks_frequency_menu.ks_menu_id.ids:
            menu = user_id.ks_frequency_menu.search([('ks_menu_id', '=', menu_id), ('ks_user_id', '=', user_id.id)])
            menu.ks_frequency = menu.ks_frequency + 1
        else:
            vals = {
                'ks_frequency': 1,
                'ks_user_id': user_id.id,
                'ks_menu_id': menu_id,
            }
            user_id.ks_frequency_menu.create(vals)

    @route(['/ks_app_frequency/render'], type='json', auth='user')
    def ks_app_frequency_render(self):
        """
        Render the list of frequently used menus
        :return: dict of top12 frequently used app by user
        """
        user_id = request.env.user
        menu_ids = user_id.ks_frequency_menu.search_read([('ks_user_id', '=', user_id.id)], ['ks_menu_id'], limit=12,
                                                         order='ks_frequency desc')
        #  ['ks_menu_id'],
        print(menu_ids)
        # return [menu['ks_menu_id'][0] for menu in menu_ids]
        return []

    # Todo: If no use then remove this function.
    @route(['/ks_curved_theme/checkbox/get'], type='json', auth='user')
    def ks_get_checkbox_style(self):
        """
        Controller to return list of selected checkbox style.
        :return:
        """

        user = request.env.user
        return user.ks_checkbox_style

    def ks_get_suntime_info(self):
        """
        Function to return sun-time info.
        :return: sun-time info
        """
        ks_current_user = request.env.user
        ks_sunrise_hour = ks_current_user.ks_sunrise_hour
        ks_sunrise_min = ks_current_user.ks_sunrise_min
        ks_sunset_hour = ks_current_user.ks_sunset_hour
        ks_sunset_min = ks_current_user.ks_sunset_min
        if ks_sunset_hour or ks_sunset_min:
            return {
                'sunrise': str(ks_sunrise_hour) + ":" + str(ks_sunrise_min) + ":00",
                'sunset': str(ks_sunset_hour) + ":" + str(ks_sunset_min) + ":00"
            }
        return False

    @route(['/ks_curved_theme/get_fav_icons'], type='json', auth='user')
    def ks_get_fav_icons(self, ks_app_icons):
        for rec in ks_app_icons:
            ks_domain = [
                ('ks_ir_ui_menu', '=', rec.get('menuID')),
                ('ks_fav_app', '=', True),
                ('ks_users', '=', request.env.user.id)
            ]
            ks_is_fav_app = request.env['ks.fav.menu'].search(ks_domain)
            rec['ks_fav_app'] = False
            if ks_is_fav_app:
                rec['ks_fav_app'] = True
        return ks_app_icons

    @route(['/ks_curved_theme/set_fav_icons'], type='json', auth='user')
    def ks_set_fav_icons(self, ks_app_id):
        ks_app_id = int(ks_app_id)
        ks_domain = [
            ('ks_ir_ui_menu', '=', ks_app_id),
            ('ks_fav_app', '=', False),
            ('ks_users', '=', request.env.user.id)
        ]
        ks_is_fav_app = request.env['ks.fav.menu'].search(ks_domain)

        if ks_is_fav_app:
            ks_is_fav_app.write({'ks_fav_app': True})
            return True
        else:
            ks_is_fav_app.create(
                {
                    'ks_fav_app': True,
                    'ks_ir_ui_menu': ks_app_id,
                    'ks_users': request.env.user.id
                }
            )
            return True

    @route(['/ks_curved_theme/rmv_fav_icons'], type='json', auth='user')
    def ks_rmv_fav_icons(self, ks_app_id):
        ks_app_id = int(ks_app_id)
        ks_domain = [
            ('ks_ir_ui_menu', '=', ks_app_id),
            ('ks_fav_app', '=', True),
            ('ks_users', '=', request.env.user.id)
        ]
        ks_is_fav_app = request.env['ks.fav.menu'].search(ks_domain)

        if ks_is_fav_app:
            ks_is_fav_app.write({'ks_fav_app': False})
            return True
        else:
            ks_is_fav_app.create(
                {
                    'ks_fav_app': False,
                    'ks_ir_ui_menu': ks_app_id,
                    'ks_users': request.env.user.id
                }
            )
            return True

    @route(['/ks_curved_theme/ks_get_website_title'], type='json', auth='public')
    def ks_get_website_title(self, **post):
        ks_origin = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
        ks_scope_value = ks_origin.scope_ks_website_title
        if ks_scope_value == 'Company':
            ks_origin = request.env.user.company_id
        # check if website title is enabled
        if ks_origin.ks_website_title_enable:
            return ks_origin.ks_website_title
        return 'Odoo'

    @route(['/kstheme/background/default'], type='json', auth='user')
    def set_background_default(self, ks_setting_scope, ks_rec_id=None, ks_default_info=None):
        if ks_setting_scope == 'Global' and ks_default_info:
            ks_global_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
            # uncheck background color.
            ks_global_obj[ks_default_info['field']] = False
            ks_global_obj[ks_default_info['field'] + '_opacity'] = 1
            # ks_global_obj.ks_body_background = False

            # de-active background image.
            ks_sel_background = request.env[ks_default_info['model']].search(
                [('ks_global', '=', True), ('ks_active', '=', True)], limit=1)
            if ks_sel_background:
                ks_sel_background.ks_active = False

        if ks_setting_scope == 'User' and ks_default_info:
            ks_user_obj = request.env.user
            ks_user_obj[ks_default_info['field']] = False
            ks_user_obj[ks_default_info['field'] + '_opacity'] = 1

            # de-active background image.
            ks_sel_background = request.env[ks_default_info['model']].search(
                [('ks_user', '=', ks_user_obj.id), ('ks_active', '=', True)], limit=1)
            if ks_sel_background:
                ks_sel_background.ks_active = False

        if ks_setting_scope == 'Company' and ks_rec_id and ks_default_info:
            ks_company_obj = request.env['res.company'].browse(ks_rec_id)
            # uncheck background color.
            ks_company_obj[ks_default_info['field']] = False
            ks_company_obj[ks_default_info['field'] + '_opacity'] = 1

            # de-active background image.
            ks_sel_background = request.env[ks_default_info['model']].search(
                [('ks_company', '=', ks_company_obj.id), ('ks_active', '=', True)], limit=1)
            if ks_sel_background:
                ks_sel_background.ks_active = False

    def ks_get_dark_mode(self):
        ks_current_user = request.env.user
        ks_sunset_hour = ks_current_user.ks_sunset_hour
        ks_sunset_min = ks_current_user.ks_sunset_min
        if ks_sunset_hour or ks_sunset_min:
            return ks_current_user.ks_auto_dark_mode
        return False

    @http.route('/ks_curved_backend_theme/getTheme', type='json', auth="user")
    def ks_get_theme(self):
        ks_color_theme_scope = request.env['ks.global.config'].ks_get_field_scope(['scope_ks_colors_theme'])
        ks_scope = ks_color_theme_scope[0].get('scope_ks_colors_theme')
        if ks_scope == 'User':
            ks_origin_obj = request.env.user
            ks_color_theme_domain = [('ks_user', '=', ks_origin_obj.id), ('ks_active', '=', True)]
        if ks_scope == 'Company':
            ks_origin_obj = request.env.user.sudo().company_id
            ks_color_theme_domain = [('ks_company', '=', ks_origin_obj.id), ('ks_active', '=', True)]
        if ks_scope == 'Global':
            ks_origin_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
            ks_color_theme_domain = [('ks_global', '=', True), ('ks_active', '=', True)]

        ks_current_theme_data = request.env['ks.color.theme'].sudo().search(ks_color_theme_domain, limit=1)
        if ks_current_theme_data:
            return {
                'primary': ks_current_theme_data.ks_primary_color,
                'body-background': ks_current_theme_data.ks_body_background,
                'nav-link-color': ks_current_theme_data.ks_menu,
                'ks-over-link': ks_current_theme_data.ks_menu_hover,
                'tab-bg': ks_current_theme_data.ks_border,
                'primary-btn': ks_current_theme_data.ks_button,
                'heading-color': ks_current_theme_data.ks_heading,
                'link-color': ks_current_theme_data.ks_link,
                'tooltip-heading-bg': ks_current_theme_data.ks_tooltip,
                'default_theme': ks_current_theme_data.ks_default
            }
        return {
            'primary': '#28C397',
            'body-background': '#ffffff',
            'nav-link-color': '#454546',
            'ks-over-link': '#f5f5f5',
            'tab-bg': '#ffffff',
            'primary-btn': '#28C397',
            'heading-color': '#28C397',
            'link-color': '#28C397',
            'tooltip-heading-bg': '#dee2e6',
            'default_theme': True
        }


class KsHome(Home):
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        request.params['ks_login_background'] = self.ks_get_login_page_image()
        res = super(KsHome, self).web_login(redirect, **kw)
        # login_status = request.params['login_success']
        # if login_status:
        #     request.env.user.partner_id.ks_set_sunrise_sunset_time()
        return res

    def ks_get_login_page_image(self):
        """
        Function to return login page background image.
        :return:
        """

        ks_global_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
        ks_back_img = ks_global_obj.sudo().ks_login_background_image
        if ks_global_obj.sudo().ks_login_background_image_enable and ks_back_img:
            return {
                'background-img': self.ks_get_image_url(ks_back_img),
                'background-opacity': ks_global_obj.sudo().ks_login_back_image_opacity
            }
        return False

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


class KsAuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        request.params['ks_login_background'] = self.ks_get_login_page_image()
        return super(KsAuthSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        request.params['ks_login_background'] = self.ks_get_login_page_image()
        return super(KsAuthSignupHome, self).web_auth_reset_password(*args, **kw)

    def ks_get_login_page_image(self):
        """
        Function to return login page background image.
        :return:
        """

        ks_global_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')
        ks_back_img = ks_global_obj.sudo().ks_login_background_image
        if ks_global_obj.sudo().ks_login_background_image_enable and ks_back_img:
            return {
                'background-img': self.ks_get_image_url(ks_back_img),
                'background-opacity': ks_global_obj.sudo().ks_login_back_image_opacity
            }
        return False

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

