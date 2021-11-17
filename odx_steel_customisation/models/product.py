# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
	_inherit = "product.product"

	
	# def _get_default_uom_id(self):
	# 	print ("self.product_tmpl_id>>>>>>>>>>.",self.product_tmpl_id)
	# 	# print ("self.product_tmpl_id>>>>>>>>>>.",self._context)
	# 	print ("self.product_tmpl_id>>>>>>>>>>.",self.env.context.get('active_id'))
	# 	print ("self.product_tmpl_id>>>>>>>>>>.",self.env.context.get('active_model'))
	# 	# if self.product_tmpl_id:
	# 	# return self.env["uom.uom"].search([], limit=1, order='id').id

	tmpl_uom_categ_id  = fields.Many2one('uom.category',related="product_tmpl_id.uom_id.category_id")
	uom_id = fields.Many2one(
		'uom.uom', 'Unit of Measure',required=True,
		help="Default unit of measure used for all stock operations.", domain="[('category_id', '=', tmpl_uom_categ_id)]")
	uom_name = fields.Char(string='Unit of Measure Name', related='uom_id.name', readonly=True)
	uom_po_id = fields.Many2one(
		'uom.uom', 'Purchase Unit of Measure', required=True,
		help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.",domain="[('category_id', '=', tmpl_uom_categ_id)]")

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			if 'uom_id' not in vals:
				vals['uom_id'] = self.env['product.template'].browse(vals.get('product_tmpl_id')).uom_id.id
			if 'uom_po_id' not in vals:
				vals['uom_po_id'] = self.env['product.template'].browse(vals.get('product_tmpl_id')).uom_po_id.id
		products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
		return products

	def update_uom_from_template(self):
		for record in self.env['product.product'].search([]):
			if record.product_tmpl_id:
				record.update({'uom_id':record.product_tmpl_id.uom_id.id})
				record.update({'uom_po_id':record.product_tmpl_id.uom_po_id.id})