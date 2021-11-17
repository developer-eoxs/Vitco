# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _compute_payment_amount(self, invoices=None, currency=None, journal=None, date=None):
        if self._context.get('active_model') == 'sale.order' and self._context.get('open_payments_so'):
            return self._context.get('default_amount', 0.0)
        else:
            return super(AccountPayment, self)._compute_payment_amount(invoices=invoices, currency=currency, journal=journal, date=date)
