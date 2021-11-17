# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    prepayment_test = fields.Boolean(
        string="Credit Testing",
        default=True,
        help="If selected then the test should be done even if the credit limit is zero.",
    )
