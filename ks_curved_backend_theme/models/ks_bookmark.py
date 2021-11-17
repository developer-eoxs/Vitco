# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class KsBookmark(models.Model):
    _name = 'ks.bookmark'
    _description = 'User Bookmarks'

    ks_bookmark_name = fields.Char(string="Bookmark Name", help="Name for displaying alphabet")
    ks_bookmark_url = fields.Char(string="Bookmark Url", help="Url of Bookmark")
    ks_bookmark_position = fields.Integer(string="Bookmark Position", default=1, help="Position of bookmark")
    ks_user_id = fields.Many2one(string="User", comodel_name="res.users", required=True, help="Connected User")