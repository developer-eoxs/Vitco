# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    x_no_of_overdue_days = fields.Integer(string='No. of Overdue Days')
