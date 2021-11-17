# -*- coding: utf-8 -*-

from odoo import models, fields, api

class OdxBreakPoint(models.Model):
	_name = 'odx.break.point'
	_description = 'Break Point'


	sale_line_id = fields.Many2one('sale.order.line', string="Sale Line")
	name = fields.Char(string="Description")
	product_id = fields.Many2one('product.product',string="Product")
	total_cost = fields.Float(string="Total Cost",compute="line_ids_change",store=True, readonly=True)
	total_markup = fields.Float(string="Total Markup",compute="line_ids_change",store=True, readonly=True)
	total_price = fields.Float(string="Total Price",compute="line_ids_change",store=True, readonly=True)
	line_ids = fields.One2many('odx.break.point.line','break_id', string="Deatils")

	@api.depends('line_ids')
	def line_ids_change(self):
		for record in self:
			cost=0
			markup=0
			price=0
			for line in record.line_ids:
				cost +=line.cost
				markup +=line.markup
				price +=line.price
			# record.cost=cost
			# record.markup=markup
			# record.price=price
			record.update({
				'total_cost': cost,
				'total_markup': markup,
				'total_price': price,
			})

	def update_markup(self):
		if self.sale_line_id:
			self.sale_line_id.markup=self.total_markup
			self.sale_line_id.product_markup_change()

	def update_unit_price(self):
		if self.sale_line_id:
			self.sale_line_id.price_unit=self.total_price
			# self.sale_line_id.product_markup_change()

class OdxBreakPointLine(models.Model):
	_name = 'odx.break.point.line'
	_description = 'Break Point Line'

	name = fields.Char(string="Description", required="1")
	cost = fields.Float(string="Cost")
	markup = fields.Float(string="Markup")
	price = fields.Float(string="Price")
	break_id = fields.Many2one('odx.break.point',string="Break Point")

	@api.onchange('markup','cost')
	def product_markup_change(self):
		self.price = self.cost*self.markup
