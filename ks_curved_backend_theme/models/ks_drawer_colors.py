# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class KsDrawerColors(models.Model):
    _name = 'ks.drawer.colors'
    _description = 'Arc Theme App Drawer Colors'

    ks_colors = fields.Char(string='Colors')
    ks_font_style = fields.Selection(selection=[('light', 'Light'), ('dark', 'Dark')],
                                     string='Font style')
    ks_no_delete = fields.Boolean(string='Default colors')
