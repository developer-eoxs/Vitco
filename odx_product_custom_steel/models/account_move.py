from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError
from itertools import groupby

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('sub_category_id', 'product_id')
    def _domain_lot_id(self):
        if self.product_id:
            return {'domain': {'lot_id': [('product_id', '=', self.product_id.id), ('stock_status', '=', 'available')]}}
        else:
            if self.sub_category_id and not self.product_id:
                return {'domain': {
                    'lot_id': [('sub_category_id', '=', self.sub_category_id.id), ('stock_status', '=', 'available')]}}

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    lot_id = fields.Many2one('stock.production.lot', string='Lot Number', domain=lambda self: self._domain_lot_id())
    produced_lot_ids = fields.Many2many('stock.production.lot', string='Lot Produced')

    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])
    # production_lot_ids = fields.One2many('steel.production', 'sale_line_id', string='Production')
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type', track_visibility="onchange")

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_default_terms(self):
        return """
            <section>
                <div class="te_sidenav_menu">
                    <ul>
                        <section>
                                1. For any issues with order please call
                        </section>
                        <section>
                                2. Please send a receipt copy of your invoice (Supplier Copy)
                        </section>
                        <section>
                               3. Unless otherwise stated, Seller agrees that the material is in good condition without
                                any known defects.
                        </section>
                    </ul>
                </div>
            </section>
        """


    shipped_via = fields.Char(string="Shipped via")
    truck_no = fields.Char(string="Truck No")
    fob_point = fields.Char(string="F.O.B. Point")
    terms_conditions = fields.Html(string='Terms & Conditions', translate=True, default=_get_default_terms)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res['category_id'] = self.category_id and self.category_id.id or False
        res['sub_category_id'] = self.sub_category_id and self.sub_category_id.id or False
        res['lot_id'] = self.lot_id and self.lot_id.id or False
        if self.produced_lot_ids:
            res['produced_lot_ids'] = [(6, 0, self.produced_lot_ids.ids)]
        res['width_in'] = self.width_in
        res['thickness_in'] = self.thickness_in
        res['length_in'] = self.length_in
        res['material_type'] = self.material_type or False

        return res
class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not invoiceable_lines and not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            # there is a chance the invoice_vals['invoice_line_ids'] already contains data when
            # another module extends the method `_prepare_invoice()`. Therefore, instead of
            # replacing the invoice_vals['invoice_line_ids'], we append invoiceable lines into it
            # odx for lot case

            # invoice_vals['invoice_line_ids'] += [
            #     (0, 0, line._prepare_invoice_line())
            #     for line in invoiceable_lines
            # ]

            for line in invoiceable_lines:
                if line.lot_id:
                    invoice_vals['invoice_line_ids'] += [(0, 0, line._prepare_invoice_line())]
                else:
                    for lot_line in line.produced_lot_ids:
                        vals =line._prepare_invoice_line()
                        if lot_line.product_qty==0:
                            vals['quantity']=lot_line.weight_lb
                        else:
                            vals['quantity']=lot_line.product_qty
                        vals['produced_lot_ids'] = [(6, 0, lot_line.ids)]
                        invoice_vals['invoice_line_ids'] += [(0, 0, vals)]
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        print ("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv",invoice_vals_list)
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves