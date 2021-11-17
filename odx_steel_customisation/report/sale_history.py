# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools,_

class OdxSaleHistory(models.Model):
    _name = 'odx.sale.history'
    _description = "Sale History"
    _auto = False

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner',string="Customer")
    markup = fields.Float(string="Markup")
    product_id = fields.Many2one('product.product',string="Product")
    purchase_price = fields.Float(string="Cost")
    price_unit = fields.Float(string="Unit Price")
    product_uom = fields.Many2one('uom.uom',string="Uom")
    product_uom_qty = fields.Float(string="Quantity")


    def init(self):
        cr = self.env.cr   
        tools.drop_view_if_exists(cr, 'odx_sale_history')
        cr.execute("""
            CREATE or replace view odx_sale_history as (
                SELECT
                    sol.id as id,
                    sol.name as name,
                    so.partner_id,
                    sol.product_id,
                    sol.markup,
                    sol.purchase_price,
                    sol.product_uom_qty,
                    sol.product_uom,
                    sol.price_unit
                    FROM sale_order_line sol
                    LEFT JOIN sale_order so ON so.id=sol.order_id
                    )
                """)  
