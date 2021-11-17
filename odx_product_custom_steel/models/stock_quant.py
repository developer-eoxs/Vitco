from odoo import models, fields, api, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    sub_category_id = fields.Many2one('product.category', string="Sub Category")

    # ,related='product_id.categ_id'

    @api.onchange('product_id')
    def _onchange_subcategory(self):
        self.sub_category_id = self.product_id.categ_id.id
