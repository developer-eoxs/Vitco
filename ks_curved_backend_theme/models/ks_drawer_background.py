# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class KsDrawerBackground(models.Model):
    _name = 'ks.drawer.background'
    _description = 'Arc Theme App Drawer Background'

    ks_image = fields.Binary(string="Image")
    ks_user = fields.Many2one(string="User", comodel_name="res.users")
    ks_company = fields.Many2one(string="Company", comodel_name="res.company")
    ks_global = fields.Boolean(string="Global")
    ks_active = fields.Boolean(string="Background selected")
