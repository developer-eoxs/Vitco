# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class KsColorTheme(models.Model):
    _name = 'ks.color.theme'
    _description = 'Arc Color Theme'

    ks_body_background = fields.Char(string='Body')
    ks_side_bar = fields.Char(string='Side Bar')
    ks_menu = fields.Char(string='Menu')
    ks_menu_hover = fields.Char(string='Menu Hover')
    ks_button = fields.Char(string='Button')
    ks_border = fields.Char(string='Border')
    ks_heading = fields.Char(string='Heading')
    ks_link = fields.Char(string='Link')
    ks_primary_color = fields.Char(string='Primary Color')
    ks_tooltip = fields.Char(string='Tooltip')

    ks_user = fields.Many2one(string="User", comodel_name="res.users")
    ks_company = fields.Many2one(string="Company", comodel_name="res.company")
    ks_global = fields.Boolean(string="Global")
    ks_active = fields.Boolean(string="Theme selected")
    ks_default = fields.Boolean(string="Default theme")
    ks_template = fields.Boolean(string="Template theme")
    ks_template_id = fields.Many2one(comodel_name='ks.color.theme', string="Connected template")
    ks_sub_theme = fields.Many2one(comodel_name='ks.color.theme', string="Related theme")
    name = fields.Char(string="Name")

    @api.model
    def get_theme(self, scope, origin):
        ks_color_theme_info = {}
        ks_color_theme = []
        ks_domain = []
        if scope == 'User':
            ks_domain = ('ks_user', '=', origin.id)
        if scope == 'Company':
            ks_domain = ('ks_company', '=', origin.id)
        if scope == 'Global':
            ks_domain = ('ks_global', '=', True)

        # Get custom themes
        ks_color_theme_info['custom'] = self.env(su=True)['ks.color.theme'].search_read(
            [('ks_template_id', '=', False), ks_domain], fields=[])

        # check if user/company has active theme if not then make default theme as active.
        ks_active_theme = self.env(su=True)['ks.color.theme'].search([ks_domain, ('ks_active', '=', True)])
        if not ks_active_theme:
            ks_default_theme = self.env(su=True)['ks.color.theme'].search([ks_domain, ('ks_default', '=', True)])
            if ks_default_theme:
                ks_default_theme.write({'ks_active': True})

        # Get pre-defined theme.
        ks_template_theme = self.env(su=True)['ks.color.theme'].search_read([('ks_template', '=', True)], fields=[])
        for temp_theme in ks_template_theme:
            ks_user_theme_temp = self.env(su=True)['ks.color.theme'].search_read(
                [('ks_template_id', '=', temp_theme['id']), ks_domain], fields=[])
            if not ks_user_theme_temp:
                vals = {
                    'ks_body_background': temp_theme['ks_body_background'],
                    'ks_menu': temp_theme['ks_menu'],
                    'ks_menu_hover': temp_theme['ks_menu_hover'],
                    'ks_button': temp_theme['ks_button'],
                    'ks_border': temp_theme['ks_border'],
                    'ks_heading': temp_theme['ks_heading'],
                    'ks_link': temp_theme['ks_link'],
                    'ks_primary_color': temp_theme['ks_primary_color'],
                    'ks_tooltip': temp_theme['ks_tooltip'],
                    'ks_template_id': temp_theme['id'],
                    'ks_active': True if temp_theme['ks_default'] else False,
                    'ks_default': True if temp_theme['ks_default'] else False,
                }
                if scope == 'User':
                    vals['ks_user'] = origin.id
                if scope == 'Company':
                    vals['ks_company'] = origin.id
                if scope == 'Global':
                    vals['ks_global'] = True

                res = self.env(su=True)['ks.color.theme'].create(vals)
                ks_color_theme += self.env(su=True)['ks.color.theme'].search_read([('id', '=', res.id)])
            else:
                ks_user_theme_temp = self.ksCheckThemeInfo(temp_theme, ks_user_theme_temp)
                ks_color_theme += ks_user_theme_temp
        ks_color_theme_info['predefined'] = ks_color_theme

        # Return theme for user and company settings.
        if scope in ['User', 'Company']:

            ks_themes = self.env(su=True)['ks.color.theme'].search_read(
                [('ks_template_id', '=', False), ('ks_global', '=', True)], fields=[])
            ks_theme_returned = ks_color_theme_info['predefined']

            # Global custom themes
            for themes in ks_themes:
                if scope == 'User':
                    ks_domain = [('ks_user', '=', origin.id), ('ks_sub_theme', '=', themes['id'])]
                    vals = {
                        'ks_user': origin.id,
                        'ks_sub_theme': themes['id']
                    }
                if scope == 'Company':
                    ks_domain = [('ks_company', '=', origin.id), ('ks_sub_theme', '=', themes['id'])]
                    vals = {
                        'ks_company': origin.id,
                        'ks_sub_theme': themes['id']
                    }
                ks_theme_obj = self.env(su=True)['ks.color.theme'].search_read(ks_domain)
                if not ks_theme_obj:
                    vals.update({
                        'ks_body_background': themes['ks_body_background'],
                        'ks_menu': themes['ks_menu'],
                        'ks_menu_hover': themes['ks_menu_hover'],
                        'ks_button': themes['ks_button'],
                        'ks_border': themes['ks_border'],
                        'ks_heading': themes['ks_heading'],
                        'ks_link': themes['ks_link'],
                        'ks_primary_color': themes['ks_primary_color'],
                        'ks_tooltip': themes['ks_tooltip'],
                        'ks_template_id': themes['id'],
                        'ks_active': True if themes['ks_default'] else False,
                        'ks_default': True if themes['ks_default'] else False,
                    })
                    self.env(su=True)['ks.color.theme'].create(vals)
                    if not ks_theme_returned:
                        ks_theme_returned = self.env(su=True)['ks.color.theme'].search_read(ks_domain)
                    else:
                        ks_theme_returned.append(self.env(su=True)['ks.color.theme'].search_read(ks_domain)[0])
                else:
                    if not ks_theme_returned:
                        ks_theme_returned = ks_theme_obj
                    else:
                        ks_theme_returned.append(ks_theme_obj[0])
            return ks_theme_returned

        return ks_color_theme_info

    def ksCheckThemeInfo(self, temp_theme, ks_user_theme_temp):
        """
        Function to check updated theme colors.
        :param temp_theme:
        :param ks_user_theme_temp:
        :return:
        """
        ks_field_check = ['ks_body_background', 'ks_menu', 'ks_menu_hover', 'ks_button', 'ks_border',
                          'ks_heading', 'ks_link', 'ks_primary_color', 'ks_tooltip', 'name'
                          ]
        ks_update_field = dict()
        for rec in ks_field_check:
            if temp_theme[rec] != ks_user_theme_temp[0][rec]:
                ks_update_field.update({rec: temp_theme[rec]})

        if len(ks_update_field):
            self.env['ks.color.theme'].sudo().search([('id', '=', ks_user_theme_temp[0]['id'])]).write(ks_update_field)
            ks_user_theme_temp = self.env['ks.color.theme'].sudo().search_read(
                [('id', '=', ks_user_theme_temp[0]['id'])])
        return ks_user_theme_temp

    def unlink(self):
        ks_shadow_theme = self.sudo().search([('ks_sub_theme', '=', self.id)])
        for rec in ks_shadow_theme:
            rec.unlink()
        return super(KsColorTheme, self).unlink()

    def write(self, vals):
        res = super(KsColorTheme, self).write(vals)
        ks_shadow_theme = self.env(su=True)['ks.color.theme'].search([('ks_sub_theme', '=', self.id)])
        for rec in ks_shadow_theme:
            rec.write(vals)
        return res
