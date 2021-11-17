# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools,_

class OdxpurchaseHistory(models.Model):
    _name = 'odx.purchase.history'
    _description = "Purchase History"
    _auto = False

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner',string="Vendor")
    product_id = fields.Many2one('product.product',string="Product")
    price_unit = fields.Float(string="Unit Price")
    product_uom = fields.Many2one('uom.uom',string="Uom")
    product_qty = fields.Float(string="Quantity")


    def init(self):
        cr = self.env.cr   
        tools.drop_view_if_exists(cr, 'odx_purchase_history')
        cr.execute("""
            CREATE or replace view odx_purchase_history as (
                SELECT
                    pol.id as id,
                    pol.name as name,
                    po.partner_id,
                    pol.product_id,
                    pol.product_qty,
                    pol.product_uom,
                    pol.price_unit
                    FROM purchase_order_line pol
                    LEFT JOIN purchase_order po ON po.id=pol.order_id
                    )
                """)  
