from datetime import date

from odoo import models, fields, api, _

from odoo.exceptions import UserError


class FreightManagement(models.Model):
    _name = 'freight.management'
    _description = 'Freight Management'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Reference', default=lambda self: self.env['ir.sequence'].next_by_code('custom.freight.sequence') or _('New'),
        required=True, readonly=True, help="Reference", copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'In transit'),
        ('done', 'Done')
    ], string='State', default='draft', track_visibility="onchange")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True,
                                       relation="res.currency")
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Reference')
    sale_order_id = fields.Many2one('sale.order', string='Sale Reference')
    job_order_id = fields.Many2one('job.order', string='Job order Reference')

    stock_picking_id = fields.Many2one('stock.picking', string='Picking Reference')
    frm_line_ids = fields.One2many('freight.line', 'freight_id', string='FRM Line')
    total_freight_price = fields.Monetary(compute='_compute_freight_amount', string='Total Freightage', store=True,
                                          currency_field='company_currency')
    assign_id = fields.Many2one('res.users', string='Assigned To', track_visibility="onchange")
    comments = fields.Char(string='Comments', track_visibility="onchange")
    cargo_lines = fields.One2many('cargo.line', 'freight_id', string="Cargo Lines")
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice")

    @api.depends('frm_line_ids.invoice_id')
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped('frm_line_ids.invoice_id')
            order.invoice_count = len(invoices)

    def action_confirm(self):
        if self.frm_line_ids:
            self.write({
                'state': 'confirm'
            })
        else:
            raise UserError(_('Please add the freight details'))

    def action_done(self):
        status_list = []
        for rec in self.frm_line_ids:
            if rec.status == 'departed' or rec.status == 'processed':
                status_list.append(rec.id)
        if status_list:
            raise UserError(_('Some freight movements are still in process.'))
        else:
            if self.stock_picking_id:
                self.stock_picking_id.is_freight_done = True
            self.write({
                'state': 'done'
            })

    def action_view_stock_pickings(self):
        picking_id_list = []
        if self.stock_picking_id:
            freight_picking = self.env['stock.picking'].search([('id', '=', self.stock_picking_id.id)])
            picking_id_list.append(freight_picking.id)

        return {
            'name': 'Stock Picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'target': 'current',
            'domain': [('id', '=', picking_id_list)],
            'type': 'ir.actions.act_window',
        }

    def action_view_purchase(self):
        orders_list = []
        if self.purchase_order_id:
            purchase_orders = self.env['purchase.order'].search([('id', '=', self.purchase_order_id.id)])
            orders_list.append(purchase_orders.id)

        return {
            'name': 'Purchase Order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'target': 'current',
            'domain': [('id', '=', orders_list)],
            'type': 'ir.actions.act_window',
        }

    def action_view_invoice(self):
        orders_list = []
        invoice_ids = self.env['account.move'].search([('freight_id', '=', self.id)])
        for inv in invoice_ids:
            orders_list.append(inv.id)
        return {
            'name': 'Vendor Bills',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'target': 'current',
            'domain': [('id', '=', orders_list)],
            'type': 'ir.actions.act_window',
        }

    @api.depends('frm_line_ids.total_price')
    def _compute_freight_amount(self):
        order_line_price = 0
        self.total_freight_price = 0
        for order in self:
            for line in order.frm_line_ids:
                order_line_price += line.total_price
            order.total_freight_price = order_line_price

    def multipoint_frm_line(self):
        for line in self.frm_line_ids:
            if line.is_multipoint_frm and line.dest_location:
                self.write({
                    'frm_line_ids': [(0, 0, {
                        'source_location': line.dest_location.id,
                        'status': 'processed',
                        'transported_lot_ids': [(4, lot.id) for lot in line.transported_lot_ids]
                    })]
                })


class FreightLine(models.Model):
    _name = 'freight.line'
    _description = 'Freight Line'

    @api.onchange('source_location', )
    def _get_lot_list(self):
        if self.freight_id.stock_picking_id:
            lots_to_transport = self.freight_id.stock_picking_id.mapped('move_line_nosuggest_ids').mapped('lot_id').ids
            fields_domain = [('id', 'in', lots_to_transport)]
            return {'domain': {'transported_lot_ids': fields_domain, }}

    name = fields.Char(string="Tracking No",
                       default=lambda self: self.env['ir.sequence'].next_by_code('freight.line') or _('New'),
                       copy=False)
    source_location = fields.Many2one('frm.location', string="Src Location")
    transporter_id = fields.Many2one('res.partner', string='Transporter', domain="[('transporter', '=', True)]")
    vehicle_ids = fields.Many2many('frm.vehicle', string='Vehicle')
    mode_id = fields.Many2one('frm.mode.operation', string='Transport Mode')
    transported_lot_ids = fields.Many2many('stock.production.lot', string='Lots',
                                           domain=[('stock_status', 'in', ['available', 'transit','in_production'])])
    # domain=lambda self: self._get_lot_list())
    freight_id = fields.Many2one('freight.management', string="Freight Id")
    dest_location = fields.Many2one('frm.location', string="Dest. Location")
    expected_date = fields.Date(string='Exp Date')
    arrived_date = fields.Date(string='Arrived Date')
    total_weight = fields.Float(string='Weight(lbs)')
    total_price = fields.Monetary(string='Freight Charge', store=True,
                                  currency_field='always_set_currency_id')
    status = fields.Selection([
        ('processed', 'Processed'),
        ('departed', 'Departed'),
        ('received', 'Received'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
    ], default='processed', string='Status')

    always_set_currency_id = fields.Many2one('res.currency', string='Foreign Currency',
                                             compute='_compute_always_set_currency_id',
                                             help="Technical field used to compute the monetary field. As currency_id is not a required field, we need to use either the foreign currency, either the company one.")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    is_multipoint_frm = fields.Boolean(string="MultiPoint Frm", default=False, copy=False)

    def send_email(self):
        self.ensure_one()
        for line in self:
            template_id = self.env.ref('odx_freight_management.mail_template_freight_eoxs').id
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            if template.lang:
                lang = template._render_template(template.lang, 'freight.line', line.ids[0])
            ctx = {
                'default_model': 'freight.line',
                'default_res_id': line.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                # 'mark_so_as_sent': True,
                # 'send_options': True,
                # 'custom_layout': "mail.mail_notification_paynow",
                # 'proforma': self.env.context.get('proforma', False),
                'force_email': True,
                'model_description': 'test',
            }
            return {
                'name': _('Send Transporter Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }

    def _compute_always_set_currency_id(self):
        for line in self:
            currency = self.env.company.currency_id.id
            line.always_set_currency_id = currency

    def update_status(self):
        if self.status == 'processed':
            self.write({
                'status': 'departed'
            })
        else:
            if self.status == 'departed':
                if not self.arrived_date:
                    self.write({
                        'status': 'received',
                        'arrived_date': date.today(),
                    })
                else:
                    self.write({
                        'status': 'received'
                    })

    def multipoint_frm_line(self):
        for line in self:
            pass

    def create_invoice(self):
        product_id = self.env['product.product'].search([('freight', '=', True)], limit=1, order='id desc')
        invoice_vals = {
            'ref': self.name or '',
            'type': 'in_invoice',
            'partner_id': self.transporter_id.id,
            'invoice_origin': self.freight_id.name,
            'freight_id': self.freight_id.id,
            'freight_line_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product_id,
                'quantity': 1,
                'price_unit': self.total_price,
            })],
        }
        invoice_id = self.env['account.move'].create(invoice_vals)
        self.write({
            'status': 'invoiced',
            'invoice_id': invoice_id.id
        })

    @api.onchange('transported_lot_ids')
    def _onchange_weight(self):
        for line in self:
            total = 0
            for lot in line.transported_lot_ids:
                if line.freight_id.stock_picking_id:
                    move_line = self.env['stock.move.line'].search(
                        [('picking_id', '=', line.freight_id.stock_picking_id.id), ('lot_id', 'in', lot.ids)])
                    if move_line:
                        # total += lot.product_qty
                        total += move_line.qty_done
                    else:
                        total += lot.product_qty
                else:
                    total += lot.product_qty
            line.total_weight = total


class CargoLines(models.Model):
    _name = 'cargo.line'
    _description = 'Cargo Details'

    freight_id = fields.Many2one('freight.management', string="Freight Id")
    product_id = fields.Many2one('product.product', string="Product")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", related='product_id.categ_id')
    name = fields.Char(string='Description', related='product_id.name')
    product_uom_qty = fields.Float('Demand', digits='Product Unit of Measure', default=0.0, )
    lot_ids = fields.Many2many('stock.production.lot', string="Lots")
