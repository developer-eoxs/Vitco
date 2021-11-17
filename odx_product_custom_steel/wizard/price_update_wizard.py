from odoo import models, fields, api


class UpdatePriceWizard(models.TransientModel):
    _name = 'update.price.wizard'

    price_line_ids = fields.One2many('sale.line.price', 'price_update_id', string='Price Line')
    sale_order_id = fields.Many2one('sale.order', "Sale Ref")

    def update_price(self):
        message = '<html> <p><b>Price Updated</b><p>'
        for rec in self.price_line_ids:
            product_lines = False
            sale_order_lines = self.sudo().mapped('sale_order_id').mapped('order_line')
            product_lines = sale_order_lines.sudo().filtered(
                lambda ol: ol.product_id.id == rec.product_id.id)
            if product_lines:
                for line in product_lines:
                    if line.price_unit != rec.price:
                        line.sudo().write(
                            {'price_unit': rec.price
                             })
                if rec.price != rec.line_price:
                    message += (
                            "<p>%s %s from Unit Price %s-->Unit Price %s </p>" % (rec.sub_category_id.name,
                                                                                  rec.product_id.name,
                                                                                  rec.line_price, rec.price))
        message += '</html>'
        # message_pool = self.env['mail.compose.message']
        subtype_id = self.env['mail.message.subtype'].search([('name', '=', 'Note')])
        self.env['mail.message'].create({
            'body': message,
            'model': 'sale.order',
            'message_type': 'comment',
            'res_id': self.sale_order_id.id,
            'subtype_id': subtype_id.id,
        })

        # self.sale_order_id.with_context({'sub_type_id': subtype_id}).message_post(body=message)
