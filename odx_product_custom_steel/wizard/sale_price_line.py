from odoo import models, fields, api


class SaleLinePrice(models.TransientModel):
    _name = 'sale.line.price'

    product_id = fields.Many2one('product.product', 'Sub Product')
    category_id = fields.Many2one('product.category', string="Master")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    line_price = fields.Float(string="Current Unit Price", digits=[6, 4])
    price = fields.Float(string="Unit Price", digits=[6, 4])
    price_update_id = fields.Many2one('update.price.wizard', string="Price wizard Reference")
