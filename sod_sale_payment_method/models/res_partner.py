# -*- coding: utf-8 -*-
# Copyright 2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_payment_method_id = fields.Many2one(
        'account.journal',
        domain=[
            ('at_least_one_inbound', '=', True),
            ('type', 'in', ['bank', 'cash'])
        ],
        string='Sale Payment Method', copy=False,
    )
