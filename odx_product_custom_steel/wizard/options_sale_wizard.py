from odoo import models, fields, api


class DisplayOptionsWizard(models.TransientModel):
    _name = 'display.options.wizard'

    memo = fields.Html('Content', readonly=True)
    sale_order_id = fields.Many2one('sale.order', "Sale Ref")
    lot_ref_id = fields.Many2one('stock.production.lot', "Lot")

    # def continue_order(self):
    #     if self.sale_order_id:
    #         self.sale_order_id.verify_options()
