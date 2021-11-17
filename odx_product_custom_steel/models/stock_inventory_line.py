from odoo import models, fields, api


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    sub_category_id = fields.Many2one('product.category', string="Sub Category", related='product_id.categ_id')
