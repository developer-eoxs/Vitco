# -*- coding: utf-8 -*-
# Copyright 2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, api, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_method_id = fields.Many2one(
        'account.journal', domain=[('at_least_one_inbound', '=', True),
            ('type', 'in', ['bank', 'cash'])
        ],
        string='Payment Method', copy=False,
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        self.payment_method_id = self.partner_id.sale_payment_method_id.id
        return res
