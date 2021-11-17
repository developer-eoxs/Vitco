from odoo import models, fields, api, _

# from odoo.exceptions import UserError
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    freight_id = fields.Many2one('freight.management', string="Freight")
    freight_line_id = fields.Many2one('freight.line', string="Freight Line")

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        for move in self:
            if move.invoice_payment_state == 'paid' and  move.freight_line_id:
                move.freight_line_id.write({ 'status': 'paid'})
        return res