from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('picking_type_id')
    def onchange_picking_type_internal(self):
        if self._context.get('is_internal_only')==True:
            return {'domain': {'picking_type_id': [('code', '=', 'internal')]}}


    @api.onchange('partner_id')
    def _get_vendor_list(self):
        if self.partner_id:
            partners = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)])
            model_fields_domain = [('id', 'in', partners.ids)]
            return {'domain': {'vendor_location_id': model_fields_domain, }}
            # return [('id', 'in', partners.ids)]

    vendor_name = fields.Char(string="Vendor Name", related="partner_id.name", readonly=True)
    vendor_serial_number = fields.Char(string="Vendor Serial Number", related="partner_id.vendor_serial_number",
                                       readonly=True)
    bill_of_lading = fields.Char(string="Bill of Lading")
    vendor_location_id = fields.Many2one('res.partner', string="Vendor Location",
                                         domain=lambda self: self._get_vendor_list())
    vendor = fields.Text(string="Vendor Note")
    category = fields.Text(string="Category")
    internal = fields.Text(string="Internal")
    is_jo_picking = fields.Boolean(string="JO Picking")

    date_removed = fields.Date(string="Date Removed")
    packing_slip_no = fields.Char(string="Packing Slip No.")

    internet_serial = fields.Char(string="R#")
    date_received = fields.Date(string="Date Received")
    po_number = fields.Char(string="PO Number")
    loc_city = fields.Char(string="Location-City")
    loc_warehouse = fields.Many2one('stock.warehouse', string="Location-Warehouse",
                                    related='picking_type_id.warehouse_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Completed'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.move_line_ids_without_package:
            for move in self.move_line_ids_without_package:
                lot = move.lot_id
                purchase = self.env['purchase.order'].search([('order_line', '=', move.move_id.purchase_line_id.id)],
                                                             limit=1)
                if purchase:
                    lot.update({
                        'vendor_name': purchase.partner_id.id,
                        # 'sale_order_id': purchase.sale_order_id.id,
                    })
                lot.update({
                    'state': 'confirm',

                })

        return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        print(self.env.context,"ppppppppp")
        if not self.env.context.get('baby_lot'):
            if self.picking_type_id.code == "outgoing":
                for line in self.move_line_ids_without_package:
                    if line.lot_id:
                        line.lot_id.stock_status = 'not_available'
            if self.picking_type_id.code == "incoming":
                for line in self.move_line_ids_without_package:
                    if line.lot_id:
                        line.lot_id.stock_status = 'available'

        return res

    def button_validate_contexted(self):
        if self.is_jo_picking:
            print("production_lot")
            return self.with_context({'production_lot': True}).button_validate()

        else:
            print("NOT production_lot")
            return self.button_validate()
