# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_view_purchase_history(self):
        action = self.env.ref('odx_steel_customisation.action_odx_purchase_history').read()[0]
        action['context'] = {
            'search_default_product_id_gr': 1,
        }
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        return action

# class PurchaseOrderLine(models.Model):
#     _inherit = "purchase.order.line"

#     no_of_quantity = fields.Float(string="No of Quantity",default=1)
#     odx_qty = fields.Float(string="Length/Weight",default=1)

#     @api.onchange('no_of_quantity','odx_qty')
#     def product_qty_change(self):
#         self.product_qty = self.no_of_quantity*self.odx_qty
