# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields, _


class PartnerCreditLimit(models.TransientModel):
    _name = 'partner.credit.limit.warning'
    _description = 'Credit Warnings'

    message = fields.Text(readonly=True)
