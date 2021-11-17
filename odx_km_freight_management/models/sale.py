# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLineInher(models.Model):
	_inherit = "sale.order.line"

	def _compute_margin(self, order_id, product_id, product_uom_id):
		frm_cur = self.env.company.currency_id
		to_cur = order_id.pricelist_id.currency_id
		purchase_price = product_id.standard_price
		if product_uom_id != product_id.uom_id:
			purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
		price = frm_cur._convert(
			purchase_price, to_cur, order_id.company_id or self.env.company,
			order_id.date_order or fields.Date.today(), round=False)
		if product_id.categ_id.property_cost_method == 'fifo':
			if self.lot_id:
		return price

