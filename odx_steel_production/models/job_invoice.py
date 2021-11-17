from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.tools import float_round


class JobOrder(models.Model):
    _inherit = 'job.order'

    invoice_id = fields.Many2one('account.move', string="Invoice", copy=False)

    def create_invoice(self):
        invoice_vals = {
            'ref': self.name or '',
            'type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [],
        }
        for line in self.multi_lot_line_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': line.product_id,
                'sub_category_id': line.sub_category_id,
                'category_id': line.category_id,
                'lot_id': line.lot_id,
                # 'material_type': line.material_type,
                'thickness_in': line.thickness_in,
                'width_in': line.width_in,
                # 'length_in': line.length_in,
                'quantity': line.product_qty,
                'product_uom_id': line.product_uom_id,
                'price_unit': line.lot_pricing,
            }))
        invoice_id = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_id': invoice_id.id
        })

    def action_view_invoice(self):
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action['context'] = {

        }
        if self.invoice_id:
            action['domain'] = [('id', '=', self.invoice_id.id)]
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = self.invoice_id.id
        return action
