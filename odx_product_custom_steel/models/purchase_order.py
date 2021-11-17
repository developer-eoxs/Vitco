from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        if self.name:
            po_number = self.env['ir.sequence'].next_by_code('purchase.serial.custom')
            self.write({
                'name': po_number
            })

        return super(PurchaseOrder, self).button_confirm()

    def _get_default_terms(self):
        return """
            <section>
                <div class="te_sidenav_menu">
                    <ul>
                        <section>
                                1. Please send a copy of your invoice.
                        </section>
                        <section>
                                2. Enter this order in accordance with the prices, terms, delivery method, and specifications listed above.
                        </section>
                        <section>
                               3. Please notify us immediately if you are unable to ship as specified.
                        </section>
                        <section>
                               4. Unless otherwise stated, Seller agrees that the material is in good condition without any known defects.
                        </section>
                        <section>
                               5. The Materials should clean and suitable for processing/slitting.
                        </section>
                    </ul>
                </div>
            </section>
        """

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New',
                       track_visibility="onchange")
    heat_number = fields.Char(string='Heat Number')
    lift_number = fields.Char(string='Lift Number')
    part_number = fields.Char(string='Part Number')
    tag_number = fields.Char(string='Tag Number')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Reference')
    offering_ids = fields.One2many('purchase.offer', 'purchase_ref_id', string='Overall Offers')
    terms_conditions = fields.Html(string='Terms & Conditions', translate=True, default=_get_default_terms)

    def select_all_lines(self):
        for line in self.offering_ids:
            line.select = True

    def un_select_all_lines(self):
        for line in self.offering_ids:
            line.select = False

    def action_clear_option_lines(self):
        offer_lines = self.offering_ids.filtered(lambda l: l.select == False)

        for rec in offer_lines:
            rec.unlink()

    def import_offer_action(self):
        return {
            'name': _('Import Offers'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.offer.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_purchase_order_id': self.id,
            }
        }

    def action_update_order_line(self):
        domain = []
        unit_price = 0
        line_object = self.env['purchase.order.line']
        line_offers = self.order_line.mapped('offer_id').ids
        order_line_products = self.order_line.mapped('product_id').ids

        option_lines = self.offering_ids.filtered(lambda l: l.select == True)

        if order_line_products:
            for line in option_lines:
                if line.product_id.id in order_line_products:
                    if line.weight_lbs:
                        # unit_price = (line.weight_lbs/100)*line.bids
                        unit_price = line.bids
                    if line.select:
                        if line.id not in line_offers:
                            for rec in self.order_line:
                                if not rec.offer_id:
                                    if line.sub_category_id.id == rec.sub_category_id.id and line.product_id.id == rec.product_id.id:
                                        new_order_line = rec.sudo().write({
                                            'order_id': self.id,
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
                                            # 'lot_id': line.lot_id.id,
                                            # 'material_type': line.lot_id.material_type
                                        })
                else:
                    return {
                        'name': _('Order Lines'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'purchase.line.wizard',
                        'views': [(False, 'form')],
                        'view_id': False,
                        'target': 'new',
                        'context': {
                            'default_purchase_order_id': self.id,
                        }
                    }
        else:
            for line in option_lines:
                if line.weight_lbs:
                    unit_price = line.bids
                new_order_line = self.order_line.sudo().create({
                    'order_id': self.id,
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


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def line_duplicate(self):
        for line in self:
            line.copy()

    @api.onchange('product_category_id')
    def _get_category_list(self):
        self.product_id = False
        if self.product_category_id:
            fields_domain = [('parent_id', '=', self.product_category_id.id)]
            return {'domain': {'sub_category_id': fields_domain, }}
        else:
            return {'domain': {'sub_category_id': []}}

    @api.onchange('cwt_price')
    def _get_cwt_based_unit_price(self):
        if self.cwt_price:
            self.price_unit = self.cwt_price / 100

    @api.onchange('category_id', 'sub_category_id')
    def _domain_product_id(self):
        if self.sub_category_id:
            return {'domain': {'product_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_id': []}}

    product_category_id = fields.Many2one('product.category', 'Category', domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", track_visibility="onchange",
                                      domain="[('parent_id', '=', product_category_id) or [] ] ")
    # domain=lambda self: self._get_category_list())
    product_template_id = fields.Many2one('product.template', 'Product Template')
    offer_id = fields.Many2one('purchase.offer', 'Offer Ref')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])
    cwt_price = fields.Float(string='CWT Price', digits=[6, 2])

    width_tolerance_min = fields.Float(string='Width Tolerance(min)', digits=[6, 4])
    width_tolerance_max = fields.Float(string='Width Tolerance(max)', digits=[6, 4])
    gauge_tolerance_min = fields.Float(string='Gauge Tolerance(min)')
    gauge_tolerance_max = fields.Float(string='Gauge Tolerance(max)')
    dia_id = fields.Float(string='ID')
    dia_od_min = fields.Float(string='OD(min)')
    dia_od_max = fields.Float(string='OD(min)')
    rockwell_min = fields.Float(string='Rockwell(min)', digits=[6, 1])
    rockwell_max = fields.Float(string='Rockwell(max)', digits=[6, 1])
    part_no = fields.Text(string='Part Number')
    fork_lift = fields.Text(string='Forklift')
    certsreq = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='CertsReq ', default='yes')
    spacers = fields.Integer(string='Spacers ')
    mx_skid_wt = fields.Char(string='Max Skid Wt.')
    over_head_crar = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Over Head Crar', default='yes')

    def action_view_purchase(self):
        action = {
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('odx_product_custom_steel.button_purchase_order_line_form').id, 'form')],
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'name': _('Purchase Order lines'),
            'res_model': 'purchase.order.line', }
        return action

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        if self.product_category_id:
            return {'domain': {'product_template_id': [('categ_id', '=', self.product_category_id.id)]}}

    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        description_picking = self.product_id.with_context(
            lang=self.order_id.dest_address_id.lang or self.env.user.lang)._get_description(
            self.order_id.picking_type_id)
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'description': self.name,
            'width_in': self.width_in,
            'thickness_in': self.thickness_in,
            'length_in': self.length_in,
            'offer_id': self.offer_id.id if self.offer_id else False,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0, precision_rounding=self.product_uom.rounding) > 0:
            po_line_uom = self.product_uom
            quant_uom = self.product_id.uom_id
            product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
            template['product_uom_qty'] = product_uom_qty
            template['product_uom'] = product_uom.id
            res.append(template)
        return res

    def _prepare_account_move_line(self, move):
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0

        return {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'move_id': move.id,
            'currency_id': move.currency_id.id,
            'purchase_line_id': self.id,
            'date_maturity': move.invoice_date_due,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'partner_id': move.commercial_partner_id.id,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'display_type': self.display_type,
            'category_id': self.product_category_id.id if self.product_category_id else False,
            'sub_category_id': self.sub_category_id.id if self.sub_category_id else False,
            'width_in': self.width_in,
            'thickness_in': self.thickness_in,
            'length_in': self.length_in,
            'material_type': 'sheets' if self.length_in > 0 else 'coil',
        }

    # @api.onchange('product_template_id')
    # def _onchange_product_template_id(self):
    #     if self.product_template_id:
    #         return {'domain': {'product_id': [('product_tmpl_id', '=', self.product_template_id.id)]}}


class PurchaseOffer(models.Model):
    _name = 'purchase.offer'

    @api.onchange('product_category_id')
    def _get_category_list(self):
        self.product_id = False
        if self.product_category_id:
            fields_domain = [('parent_id', '=', self.product_category_id.id)]
            return {'domain': {'sub_category_id': fields_domain, }}
        else:
            return {'domain': {'sub_category_id': []}}

    @api.onchange('category_id', 'sub_category_id')
    def _domain_product_id(self):
        if self.sub_category_id:
            return {'domain': {'product_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_id': []}}

    def line_duplicate(self):
        for line in self:
            line.copy()

    product_category_id = fields.Many2one('product.category', 'Category', domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", track_visibility="onchange",
                                      domain="[('parent_id', '=', product_category_id) or [] ] ")
    product_id = fields.Many2one('product.product', 'Sub Product',
                                 domain="[('categ_id', '=', sub_category_id) or [] ] ")
    # is_present = fields.Boolean(string="Is Present")
    name = fields.Char(string="Name")
    select = fields.Boolean(string="Select")
    bids = fields.Float(string="Bids", digits=[8, 4])
    product_group = fields.Char(string="Product Group")
    material = fields.Char(string="Material")
    batch = fields.Char(string="Batch")
    gauge = fields.Float(string="Gauge", digits=[8, 4])
    width_in = fields.Float(string="Width(in)", digits=[8, 4])
    weight_lbs = fields.Float(string="Weight(lbs)")

    ordered_grade = fields.Char(string="Ordered Grade")
    comment = fields.Char(string="Comment")
    notes = fields.Char(string="Notes")
    length_ft = fields.Integer(string="Length(ft.)")
    inner_dia = fields.Float(string="ID")
    outer_dia = fields.Float(string="OD")
    heat_number = fields.Char(string="Heat Number")

    comp_c = fields.Float(string="C", digits=[4, 3])
    comp_mn = fields.Float(string="MN", digits=[4, 3])
    comp_p = fields.Float(string="P", digits=[4, 3])
    comp_s = fields.Float(string="S", digits=[4, 3])
    comp_si = fields.Float(string="SI", digits=[4, 3])
    comp_al = fields.Float(string="AL", digits=[4, 3])
    comp_al_total = fields.Float(string="AL Total", digits=[4, 3])
    comp_nb = fields.Float(string="NB", digits=[4, 3])
    comp_ti = fields.Float(string="TI", digits=[4, 3])
    comp_b = fields.Float(string="B", digits=[4, 3])
    comp_cu = fields.Float(string="CU", digits=[4, 3])
    comp_as = fields.Float(string="As", digits=[4, 3])
    comp_co = fields.Float(string="Co", digits=[4, 3])
    comp_cr = fields.Float(string="Cr", digits=[4, 3])

    comp_mo = fields.Float(string="Mo", digits=[4, 3])
    comp_n = fields.Float(string="N", digits=[4, 3])
    comp_ni = fields.Float(string="NI", digits=[4, 3])
    comp_v = fields.Float(string="V", digits=[4, 3])
    comp_pb = fields.Float(string="Pb", digits=[4, 3])
    comp_ca = fields.Float(string="CA", digits=[4, 3])

    purchase_ref_id = fields.Many2one('purchase.order', string="Purchase Reference")
