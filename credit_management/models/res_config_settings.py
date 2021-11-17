# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    add_prepayment_test = fields.Boolean(
        string="Add Prepayment Test",
        config_parameter='credit_management.prepayment_test',
        help="If selected then the test should be done even if the credit limit is zero."
    )

    no_of_days_overdue_test = fields.Boolean(
        string="Add Overdue Days Test",
        config_parameter="credit_management.no_of_days_overdue_test",
        help="If selected then the test should be done for the number of days overdue."
    )

    x_no_of_overdue_days = fields.Integer(
        string='No. Of Overdue Days',
        config_parameter='credit_management.x_no_of_overdue_days',
        readonly=False
    )
