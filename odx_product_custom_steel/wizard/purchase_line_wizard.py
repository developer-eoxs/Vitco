from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseLineWizard(models.TransientModel):
    _name = 'purchase.line.wizard'

    # name = fields.Char('name')
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Reference")

    def action_generate_order_line(self):
        domain = []
        unit_price = 0
        line_object = self.env['purchase.order.line']
        line_offers = self.purchase_order_id.order_line.mapped('offer_id').ids
        order_line_products = self.purchase_order_id.order_line.mapped('product_id').ids

        option_lines = self.purchase_order_id.offering_ids.filtered(lambda l: l.select == True)

        for line in option_lines:
            if line.product_id.id in order_line_products:
                if line.weight_lbs:
                    # unit_price = line.bids / line.weight_lbs
                    unit_price = line.bids
                if line.select:
                    if line.id not in line_offers:
                        for rec in self.purchase_order_id.order_line:
                            if not rec.offer_id:
                                if line.sub_category_id.id == rec.sub_category_id.id and line.product_id.id == rec.product_id.id:
                                    new_order_line = rec.sudo().write({
                                        'order_id': self.purchase_order_id.id,
                                        # 'product_id': line.product_id.id,
                                        # 'product_category_id': line.product_category_id.id,
                                        # 'sub_category_id': line.sub_category_id.id,
                                        'product_qty': line.weight_lbs,
                                        'product_uom': line.product_id.uom_id.id,
                                        'price_unit': unit_price,
                                        'offer_id': line.id,
                                        'date_planned': fields.Datetime.now(),
                                        'name': line.name if line.name else line.product_id.name,
                                        'thickness_in': line.gauge,
                                        'width_in': line.width_in,

                                    })
            else:
                if line.weight_lbs:
                    unit_price = line.bids
                new_order_line = self.purchase_order_id.order_line.sudo().create({
                    'order_id': self.purchase_order_id.id,
                    'product_id': line.product_id.id,
                    'product_category_id': line.product_category_id.id,
                    'sub_category_id': line.sub_category_id.id,
                    'product_qty': line.weight_lbs,
                    'product_uom': line.product_id.uom_id.id,
                    'price_unit': unit_price,
                    'offer_id': line.id,
                    'date_planned': fields.Datetime.now(),
                    'name': line.name if line.name else line.product_id.name,
                    'thickness_in': line.gauge,
                    'width_in': line.width_in,

                })
