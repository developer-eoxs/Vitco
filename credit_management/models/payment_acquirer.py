# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import api, fields, models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _check_or_create_sale_tx(self, order, acquirer, payment_token=None, tx_type='form', add_tx_values=None, reset_draft=True):
        tx = super(PaymentTransaction, self)._check_or_create_sale_tx(
            order, acquirer, payment_token=payment_token, tx_type=tx_type, add_tx_values=add_tx_values, reset_draft=reset_draft)
        tx = tx.with_context(website_order_tx=True)
        return tx
