# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round


class SteelProduction(models.Model):
    _name = 'steel.production'
    _description = 'Steel Production'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('steel.production.sequence') or _('New')
        return super(SteelProduction, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('steel.production.sequence') or _('New')

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.category_id = self.lot_id.category_id.id if self.lot_id.category_id else False
        self.sub_category_id = self.lot_id.sub_category_id.id if self.lot_id.sub_category_id else False
        self.product_id = self.lot_id.product_id.id if self.lot_id.product_id else False
        self.product_qty = self.lot_id.product_qty
        self.width_in = self.lot_id.width_in
        self.thickness_in = self.lot_id.thickness_in
        self.product_uom_id = self.lot_id.product_uom_id.id if self.lot_id.product_uom_id else False
        self.material_type = self.lot_id.material_type
        self.lot_status = self.lot_id.stock_status

    def _get_default_ftechnical_delivery_cond(self):
        return """
            <section>
                <div class="te_sidenav_menu">
                    <ul>
                        <section>
                                1. Gauge range :
                        </section>
                        <section>
                                2. Width Tolerance : 
                        </section>
                        <section>
                               3. Length Tolerance:
                        </section>
                    </ul>
                </div>
            </section>
        """

    def _get_default_terms(self):
        return """
            <section>
                <div class="te_sidenav_menu">
                    <ul>
                        <section>
                                1. For any issues with order please call
                        </section>
                        <section>
                                2. Please Tag as per the Finished Goods Specification.
                        </section>
                        <section>
                               3. Please send a copy of your invoice.
                        </section>
                        <section>
                               4. Enter this order in accordance with the prices, terms, delivery method, and specifications listed above.
                        </section>
                    </ul>
                </div>
            </section>
        """

    name = fields.Char(
        'Reference', default=lambda self: _('New'),
        required=True, readonly=True, copy=False, help="Reference")
    # name = fields.Char(
    #     'Reference', default=lambda self: self.env['ir.sequence'].next_by_code('steel.production.sequence'),
    #     required=True, readonly=True, help="Reference")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='State', default='draft', track_visibility="onchange")

    operation = fields.Selection([
        ('slitting', 'Slitting'),
        ('cutting', 'Cut to Length'),
        ('parting', 'Break for Weight(Parting)'),
        ('multistage', 'Blanking(MultiStage)'),
        ('multistage_slitting', 'MultiStage Slitting'),
        ('annealing', 'Annealing'),
        ('cr', 'Cold Rolling'),
        ('degreasing', 'DeGreasing'),
        ('tr', 'Temper Rolling'),
        ('pickling', 'Pickling'),

    ], string='Operation', required=True, default='slitting', track_visibility="onchange")
    prod_due_date = fields.Date(string="Due Date")
    prod_event_date = fields.Datetime(string="Work Event Date")
    second_operation = fields.Selection([
        ('cutting', 'Cut to Length'),
        ('parting', 'Parting'),
    ], string='Second Stage Operation', required=True, default='parting', track_visibility="onchange")

    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type', track_visibility="onchange")
    lot_status = fields.Selection([
        ('transit', 'In Transit'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('not_available', 'Not available')
    ], string='Stock Status', track_visibility="onchange")

    description = fields.Char(string='Description')

    req_width = fields.Float(string='Width(in)', digits=[6, 4])
    req_thickness = fields.Float(string='Thickness(in)', digits=[6, 4])
    req_length = fields.Float(string='Length(in)', digits=[6, 4])
    # req_number_of_sheets = fields.Float(string='No.of Sheets')
    req_weight = fields.Float(string='Weight(lbs)')
    req_material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')
    number_of_parts = fields.Integer(string='No.Of Parts')
    number_of_bundles = fields.Integer(string='No.Of Bundles', default=1)

    sale_line_id = fields.Many2one(comodel_name='sale.order.line', string="Order Line")
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Order Ref")

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Lot", track_visibility='onchange',
                             domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available')])
    second_run_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Lot", track_visibility='onchange',
                                        domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available')])
    picking_id = fields.Many2one('stock.picking', string='Picking')
    finished_picking_id = fields.Many2one('stock.picking', string='Finished Picking')
    finished_move_id = fields.Many2one('stock.move', string='Stock Move')
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]",
                                  track_visibility="onchange")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", track_visibility="onchange")
    product_id = fields.Many2one('product.product', string='Sub Product', track_visibility="onchange")
    product_qty = fields.Float(string='Weight', track_visibility='onchange')
    width_in = fields.Float(string='Width(in)', track_visibility='onchange')
    thickness_in = fields.Float(string='Thickness(in)', track_visibility='onchange', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom', track_visibility='onchange')
    production_line_ids = fields.One2many('steel.production.line', 'production_ref_id', string="Production Line")
    multi_stage_line_ids = fields.One2many('multi.stage.line', 'production_stage_id', string="Multi Stage Line")
    lot_skid_line_ids = fields.One2many('lot.skid', 'production_skid_id', string="Lot Skids")
    pro_multi_lot_line_ids = fields.One2many('pro.multi.lot.line', 'pro_ref_id', string="Multi Lot Lines")
    order_line_product = fields.Many2one('product.product', string='OrderLine Product')
    dest_warehouse_id = fields.Many2one('stock.warehouse', 'Dest. Warehouse',
                                        required=True)
    instruction_id = fields.Many2one('production.instructions', string='Instruction Ref')
    instruction_line_id = fields.Many2one('instructions.run.line', string='Instruction Line Ref')

    coil_processing_details = fields.Html(string="Coil Processing Details", translate=True)
    technical_delivery_cond = fields.Html(string="Technical Delivery Conditions", translate=True,
                                          default=_get_default_ftechnical_delivery_cond)
    terms_conditions = fields.Html(string='Terms & Conditions', translate=True, default=_get_default_terms)
    scrap_percent = fields.Float(string='Scrap Percent',)
    # compute = 'scrap_percentage'

    # def scrap_percentage(self):
    #     scrap_wt = 0
    #     self.scrap_percent = 0
    #     for lots in self:
    #         if lots.multi_stage_line_ids:
    #             for rec in lots.multi_stage_line_ids:
    #                 if rec.is_scrap:
    #                     scrap_wt += rec.product_qty
    #         if lots.production_line_ids:
    #             for line in lots.production_line_ids:
    #                 if line.is_scrap:
    #                     scrap_wt += line.product_qty
    #         if lots.instruction_id.product_qty > 0:
    #             lots.scrap_percent = (scrap_wt / lots.instruction_id.product_qty) * 100
    #         print(lots.scrap_percent)
    #         print(lots.instruction_id.product_qty)

    def action_confirm(self):
        for line in self.production_line_ids:
            if line.product_qty <= 0:
                raise UserError(
                    _("Weight is not Provided in line"))
        if not self.sale_order_id:
            for lot in self.pro_multi_lot_line_ids:
                lot.lot_id.stock_status = 'in_production'
                lot.lot_status = 'in_production'

        for tags in self.pro_multi_lot_line_ids:
            line_width = line_weight = residue_width = residue_weight = multi_stage_width = multi_stage_weight = 0
            multistage_residue_width = multistage_residue_wt = 0
            for lines in self.production_line_ids:
                if tags.lot_id == lines.lot_id:
                    line_width += lines.width_in
                    line_weight += lines.product_qty

            if self.operation == 'multistage':
                for stage_lines in self.multi_stage_line_ids:
                    if tags.lot_id == stage_lines.lot_id:
                        multi_stage_width += stage_lines.width_in
                        multi_stage_weight += stage_lines.product_qty
                        # multi_stage_weight += sum(self.mapped('multi_stage_line_ids').mapped('product_qty'))

            residue_width = tags.width_in - line_width
            residue_weight = tags.product_qty - line_weight
            print(residue_weight)
            multistage_residue_width = tags.width_in - multi_stage_width
            multistage_residue_wt = tags.product_qty - multi_stage_weight

            # line_width = line_weight = residue_width = residue_weight = multi_stage_width = multi_stage_weight = 0
            # multistage_residue_width = multistage_residue_wt = 0
            # line_width = sum(self.mapped('production_line_ids').mapped('width_in'))
            # line_weight = sum(self.mapped('production_line_ids').mapped('product_qty'))

            if self.operation == 'slitting' or self.operation == 'annealing':
                if (line_width <= tags.width_in):
                    if (line_weight <= tags.product_qty):
                        if line_width < tags.width_in or line_weight < tags.product_qty:
                            # if (line_width <= tags.width_in) and (line_weight <= tags.product_qty):
                            #     if line_width < tags.width_in and line_weight < tags.product_qty:
                            self.write({
                                'production_line_ids': [(0, 0, {
                                    'lot_id': tags.lot_id.id,
                                    'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                                    'category_id': tags.category_id.id,
                                    'sub_category_id': tags.sub_category_id.id,
                                    'product_qty': residue_weight,
                                    'product_uom_id': tags.product_uom_id.id,
                                    'thickness_in': tags.thickness_in,
                                    'material_type': 'coil',
                                    'width_in': residue_width,
                                    'lot_status': 'available',
                                    'is_balance': True,

                                })]
                            })
                        self.write({'state': 'confirm'})
                    else:
                        raise UserError(_("Sum of the weights exceeded the Coil Weight for %s" % tags.lot_id.name))
                        # self.write({'state': 'confirm'})
                else:
                    raise UserError(_("Sum of the widths exceeded the Coil Width for %s" % tags.lot_id.name))

            elif self.operation == 'multistage':

                for multi_line in self.multi_stage_line_ids:
                    if multi_line.lot_id == tags.lot_id:
                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': multi_line.lot_id.id,
                                'product_id': multi_line.product_id.id,
                                'category_id': multi_line.category_id.id,
                                'sub_category_id': multi_line.sub_category_id.id,
                                'product_qty': multi_line.product_qty,
                                'product_uom_id': multi_line.product_uom_id.id,
                                'thickness_in': multi_line.thickness_in,
                                'material_type': 'sheets' if self.second_operation == 'cutting' else 'coil',
                                'width_in': multi_line.width_in,
                                'lot_status': 'available',
                            })]

                        })

                if (multi_stage_width <= tags.width_in) and (multi_stage_weight <= tags.product_qty):
                    if multi_stage_width < tags.width_in and multi_stage_weight < tags.product_qty:
                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': tags.lot_id.id,
                                'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                                'category_id': tags.category_id.id,
                                'sub_category_id': tags.sub_category_id.id,
                                'product_qty': multistage_residue_wt,
                                'product_uom_id': tags.product_uom_id.id,
                                'thickness_in': tags.thickness_in,
                                'material_type': 'coil',
                                'width_in': multistage_residue_width,
                                'lot_status': 'available',
                                'is_balance': True,

                            })]
                        })
                        self.write({'state': 'confirm'})
                    else:
                        self.write({'state': 'confirm'})
                else:
                    raise UserError(_("Sum of the widths exceeded the Coil Width"))

            elif self.operation == 'parting':
                if line_weight <= tags.product_qty:
                    bal_width_in = 0
                    if line_weight < tags.product_qty:
                        if residue_width > 0:
                            bal_width_in = residue_width
                        else:
                            bal_width_in = tags.width_in

                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': tags.lot_id.id,
                                'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                                'category_id': tags.category_id.id,
                                'sub_category_id': tags.sub_category_id.id,
                                'product_qty': residue_weight,
                                'product_uom_id': tags.product_uom_id.id,
                                'thickness_in': tags.thickness_in,
                                'material_type': 'coil',
                                'width_in': bal_width_in,
                                'lot_status': 'available',
                                'is_balance': True,
                            })]
                        })
                        self.write({'state': 'confirm'})
                    else:
                        self.write({'state': 'confirm'})
                else:
                    raise UserError(_("Sum of the Weights exceeded the Coil Weight"))

            else:
                if self.operation == 'cutting':
                    width_balance = tags.width_in
                else:
                    width_balance = residue_width

                if line_weight <= tags.product_qty:
                    if line_weight < tags.product_qty:
                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': tags.lot_id.id,
                                'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                                'category_id': tags.category_id.id,
                                'sub_category_id': tags.sub_category_id.id,
                                'product_qty': residue_weight,
                                'product_uom_id': tags.product_uom_id.id,
                                'thickness_in': tags.thickness_in,
                                'material_type': 'coil',
                                'width_in': width_balance,
                                'lot_status': 'available',
                                'is_balance': True,
                            })]
                        })
                        self.write({'state': 'confirm'})
                    else:
                        self.write({'state': 'confirm'})
                else:
                    raise UserError(_("Sum of the Weights exceeded the Coil Weight"))

    def action_confirm_ms_slitting(self):
        for line in self.production_line_ids:
            if line.product_qty <= 0:
                raise UserError(
                    _("Weight is not Provided in line"))
            else:
                self.state = "confirm"

    def create_second_run_picking(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id)])
        production_location = self.env['stock.location'].search([('usage', '=', 'production'),
                                                                 ('company_id', '=',
                                                                  self.env.company.id)],
                                                                limit=1)
        dest_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
             ('warehouse_id', '=', self.dest_warehouse_id.id)])

        dest_wh_location = self.env.ref('stock.stock_location_stock').id
        dest_wh = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_wh_location)])

        if self.second_run_lot_id:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
                 ('warehouse_id', '=', self.second_run_lot_id.loc_warehouse.id)])

            picking_source_id = self.env['stock.picking'].create({
                'location_id': self.second_run_lot_id.loc_warehouse.lot_stock_id.id,
                'location_dest_id': production_location.id,
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,

            })
            # self.picking_id = picking_source_id
            move = self.env['stock.move'].create({
                'name': self.second_run_lot_id.product_id.name,
                'product_id': self.second_run_lot_id.product_id.id,
                'product_uom_qty': self.second_run_lot_id.product_qty,
                'product_uom': self.second_run_lot_id.product_uom_id.id,
                'picking_id': picking_source_id.id,
                'location_id': self.second_run_lot_id.loc_warehouse.lot_stock_id.id,
                'location_dest_id': production_location.id,
                # 'location_id': self.env.ref('stock.stock_location_stock').id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,
                # self.env.ref('stock.picking_type_internal').id,
            })
            move_line_id = self.env['stock.move.line'].create(move._prepare_move_line_vals())

            for line in move_line_id:
                line.lot_id = self.second_run_lot_id.id
                line.lot_name = self.second_run_lot_id.name
                line.qty_done = self.second_run_lot_id.product_qty
            picking_source_id.button_validate()

            self.second_run_lot_id.stock_status = 'not_available'

            self.second_run_lot_id.process_done = 'slitting'
            if self.operation == 'annealing':
                self.second_run_lot_id.is_annealed = 'yes'

            # self.lot_id.stock_status = 'not_available'

        if self.production_line_ids:
            product = []
            for line in self.production_line_ids:
                if not line.is_scrap:
                    product.append(line)
            finished_picking = self.env['stock.picking'].create({
                'location_id': production_location.id,
                'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                'picking_type_id': dest_picking_type.id,
                'company_id': self.env.company.id,
                # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                # 'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_id': self.env.ref('stock.picking_type_internal').id,

            })
            self.finished_picking_id = finished_picking.id

            for products in product:
                move_lines_list = []
                new_move_list = []
                status_stock = ''
                i = bundle_quantity = 0
                sheet_numbers = 0

                if products.product_qty:
                    move = self.env['stock.move'].create({
                        'name': products.product_id.name,
                        'product_id': products.product_id.id,
                        'product_uom_qty': products.product_qty,
                        'product_uom': products.product_uom_id.id,
                        'picking_id': finished_picking.id,
                        # 'location_id': self.env.ref('stock.picking_type_internal').id,
                        'location_id': production_location.id,
                        'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                        # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,

                    })
                    self.finished_move_id = move.id
                lot_ids = []

                # sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
                rounding = products.product_uom_id.rounding
                qty = float_round(products.product_qty, precision_rounding=rounding)
                if products.production_ref_id.sale_order_id:
                    if products.is_balance == False:
                        status_stock = 'reserved'
                    else:
                        status_stock = 'available'
                else:
                    status_stock = 'available'

                new_lots = self.env['stock.production.lot'].with_context({'baby_lot': True}). \
                    create(
                    {'name': _('New'),
                     'product_id': products.product_id.id,
                     'company_id': self.env.company.id,
                     'sub_category_id': products.product_id.categ_id.id,
                     'category_id': products.product_id.categ_id.parent_id.id,
                     'product_qty': qty,
                     'weight_lb': products.product_qty,
                     'product_uom_id': products.product_uom_id.id,
                     'thickness_in': products.thickness_in,
                     'width_in': products.width_in,
                     'length_in': products.length_in if products.material_type == 'sheets' else 0,
                     'material_type': products.material_type,
                     'number_of_sheets': products.number_of_sheets if products.material_type == 'sheets' else 0,
                     'is_child_coil': True,
                     'parent_coil_id': products.lot_id.id,
                     'stock_status': status_stock,
                     'bill_of_lading': products.lot_id.bill_of_lading,
                     'vendor_id': products.lot_id.vendor_id.id if products.lot_id.vendor_id else False,
                     # 'vendor_location_id': products.lot_id.vendor_location_id.id if products.lot_id.vendor_location_id else False,
                     'vendor_serial_number': products.lot_id.vendor_serial_number,
                     'thickness_spec': products.lot_id.thickness_spec,
                     'rockwell': products.lot_id.rockwell,
                     'yield_mpa': products.lot_id.yield_mpa,
                     'elongation': products.lot_id.elongation,
                     'tensile_mpa': products.lot_id.tensile_mpa,
                     'date_received': products.lot_id.date_received,

                     'internet_serial': products.lot_id.internet_serial,
                     'packing_slip_no': products.lot_id.packing_slip_no,
                     'comp_c': products.lot_id.comp_c,
                     'comp_mn': products.lot_id.comp_mn,
                     'comp_p': products.lot_id.comp_p,
                     'comp_s': products.lot_id.comp_s,
                     'comp_si': products.lot_id.comp_si,
                     'comp_al': products.lot_id.comp_al,
                     'comp_cr': products.lot_id.comp_cr,
                     'comp_nb': products.lot_id.comp_nb,
                     'comp_ti': products.lot_id.comp_ti,
                     'comp_ca': products.lot_id.comp_ca,
                     'comp_n': products.lot_id.comp_n,
                     'comp_ni': products.lot_id.comp_ni,
                     'comp_cu': products.lot_id.comp_cu,
                     'comp_v': products.lot_id.comp_v,
                     'comp_b': products.lot_id.comp_b,
                     'pass_oil': products.lot_id.pass_oil,
                     'finish': products.lot_id.finish,
                     'temper': products.lot_id.temper,
                     'category': products.lot_id.category,
                     'coating': products.lot_id.coating,
                     'heat_number': products.lot_id.heat_number,
                     'lift_number': products.lot_id.lift_number,
                     'part_number': products.lot_id.part_number,
                     'tag_number': products.lot_id.tag_number,
                     'grade': products.lot_id.grade,
                     'quality': products.lot_id.quality,
                     'loc_city': self.dest_warehouse_id.lot_stock_id.id,
                     'loc_warehouse': self.dest_warehouse_id.id,
                     # 'loc_city': self.env.ref('stock.stock_location_stock').id,
                     # 'loc_warehouse': dest_wh.id,
                     'po_number': products.lot_id.po_number,
                     'is_annealed': 'yes' if self.operation == 'annealing' else 'no',
                     'purchase_cost': products.lot_id.purchase_cost + products.lot_id.landed_cost,
                     'total_purcahse_cost': (products.lot_id.purchase_cost + products.lot_id.landed_cost) * qty,

                     })
                new_lots._onchange_width()
                new_lots._onchange_thickness()
                new_lots._onchange_length()
                lot_ids.append(new_lots)
                products.finished_lot_id = new_lots.id
                products.lot_status = new_lots.stock_status
                move_line_id = self.env['stock.move.line'].create(
                    move._prepare_move_line_vals())

                for line in move_line_id:
                    line.lot_id = new_lots.id
                    line.qty_done = qty
                    new_move_list = line.id

            try:
                finished_picking.action_confirm()
            except:
                pass
            finished_picking.with_context({'baby_lot': True}).button_validate()
            self.write({'state': 'done'})
            # self.lot_status = 'not_available'
            # if self.sale_order_id:
            #     print('fg')
            #     return self.action_create_picking()

    def action_cancel(self):
        if self.user_has_groups('odx_steel_production.group_steel_production_manager'):
            return {
                'name': _('Cancel Production'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'production.cancel.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_production_id': self.id,
                }
            }

        else:
            raise UserError(_('You do not have the permission to Cancel.Please Contact Administrator.'))

    def add_product_to_line(self):
        if self.lot_id:
            if self.operation == 'parting':
                if self.number_of_parts > 0:
                    i = 0
                    while i < self.number_of_parts:
                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                # 'product_id': self.product_id.id,
                                'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                                'category_id': self.category_id.id,
                                'sub_category_id': self.sub_category_id.id,
                                # 'product_qty': self.product_qty / self.number_of_parts,
                                'product_uom_id': self.product_uom_id.id,
                                'thickness_in': self.thickness_in,
                                'material_type': 'coil',
                                'width_in': self.width_in / self.number_of_parts,

                            })]
                        })
                        i += 1
            elif self.operation == 'cutting':
                if self.number_of_bundles > 0:
                    i = 0
                    while i < self.number_of_bundles:
                        self.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                # 'product_id': self.product_id.id,
                                'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                                'category_id': self.category_id.id,
                                'sub_category_id': self.sub_category_id.id,
                                # 'product_qty': self.product_qty / self.number_of_parts,
                                'product_uom_id': self.product_uom_id.id,
                                'thickness_in': self.thickness_in,
                                'material_type': 'sheets',
                                'width_in': self.width_in,

                            })]
                        })
                        i += 1
            elif self.operation == 'multistage':
                if self.state == 'draft':
                    self.write({
                        'multi_stage_line_ids': [(0, 0, {
                            'lot_id': self.lot_id.id,
                            # 'product_id': self.product_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                            'category_id': self.category_id.id,
                            'sub_category_id': self.sub_category_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'thickness_in': self.thickness_in,
                            'material_type': 'coil',
                            # 'width_in': self.width_in,

                        })]
                    })

                else:

                    self.write({
                        'production_line_ids': [(0, 0, {
                            'lot_id': self.lot_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                            # 'product_id': self.product_id.id,
                            'category_id': self.category_id.id,
                            'sub_category_id': self.sub_category_id.id,
                            'product_uom_id': self.product_uom_id.id,
                            'thickness_in': self.thickness_in,
                            'material_type': 'sheets' if self.second_operation == 'cutting' else 'coil',
                            # 'width_in': self.width_in,

                        })]
                    })

            elif self.operation == 'annealing':
                self.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        'product_uom_id': self.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'material_type': 'coil',
                        'width_in': self.width_in,
                        'product_qty': self.product_qty,

                    })]
                })
            elif self.operation == 'cr':
                self.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        'product_uom_id': self.product_uom_id.id,
                        # 'thickness_in': self.thickness_in,
                        'material_type': 'coil',
                        'width_in': self.width_in,
                        # 'product_qty': self.product_qty,

                    })]
                })
            else:
                self.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.order_line_product.id if self.order_line_product else self.product_id.id,
                        # 'product_id': self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        # 'product_qty': self.product_qty,
                        'product_uom_id': self.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'material_type': 'sheets' if self.operation == 'cutting' else 'coil',
                        'width_in': self.width_in,

                    })]
                })

    def add_line(self):
        for tags in self.pro_multi_lot_line_ids:
            if self.second_operation == 'parting' and tags.number_of_parts > 0:
                i = 0
                while i < tags.number_of_parts:
                    self.write({
                        'production_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                            # 'product_id': self.product_id.id,
                            'category_id': tags.category_id.id,
                            'sub_category_id': tags.sub_category_id.id,
                            # 'product_qty': self.product_qty,
                            'product_uom_id': tags.product_uom_id.id,
                            'thickness_in': tags.thickness_in,
                            'material_type': 'coil',
                            'lot_status': 'reserved' if self.sale_order_id else 'available',

                        })]
                    })
                    i += 1
            if self.second_operation == 'cutting' and tags.number_of_bundles > 0:
                i = 1
                while i < tags.number_of_bundles:
                    self.write({
                        'production_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
                            # 'product_id': self.product_id.id,
                            'category_id': tags.category_id.id,
                            'sub_category_id': tags.sub_category_id.id,
                            # 'product_qty': self.product_qty,
                            'product_uom_id': tags.product_uom_id.id,
                            'thickness_in': tags.thickness_in,
                            'material_type': 'sheets',
                            'lot_status': 'reserved' if self.sale_order_id else 'available',

                        })]
                    })
                    i += 1

    def add_scrap_line(self):
        for tags in self.pro_multi_lot_line_ids:
            balance_wt = 0
            line_weight = 0
            for lines in self.production_line_ids:
                if tags.lot_id == lines.lot_id:
                    line_weight += lines.product_qty

            balance_wt = tags.product_qty - line_weight
            if line_weight < tags.product_qty:
                self.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': tags.lot_id.id,
                        'product_id': tags.product_id.id,
                        # 'product_id': self.product_id.id,
                        'category_id': tags.category_id.id,
                        'sub_category_id': tags.sub_category_id.id,
                        'product_qty': balance_wt,
                        'product_uom_id': tags.product_uom_id.id,
                        'thickness_in': tags.thickness_in,
                        'material_type': 'sheets',
                        'lot_status': 'available',
                        'is_scrap': True,

                    })]
                })

    def action_reset_to_draft(self):
        if self.state == 'confirm':
            self.write({
                'state': 'draft'
            })
            self.production_line_ids = False
            for rec in self.pro_multi_lot_line_ids:
                rec.lot_id.stock_status = 'available'
                rec.lot_status = 'available'

    def create_multi_stage_picking(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id)])
        production_location = self.env['stock.location'].search([('usage', '=', 'production'),
                                                                 ('company_id', '=',
                                                                  self.env.company.id)],
                                                                limit=1)
        dest_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
             ('warehouse_id', '=', self.dest_warehouse_id.id)])

        dest_wh_location = self.env.ref('stock.stock_location_stock').id
        dest_wh = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_wh_location)])

        for lots in self.pro_multi_lot_line_ids:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
                 ('warehouse_id', '=', lots.src_warehouse_id.id)])

            picking_source_id = self.env['stock.picking'].create({
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,

            })
            # self.picking_id = picking_source_id
            move = self.env['stock.move'].create({
                'name': lots.product_id.name,
                'product_id': lots.product_id.id,
                'product_uom_qty': lots.product_qty,
                'product_uom': lots.product_uom_id.id,
                'picking_id': picking_source_id.id,
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                # 'location_id': self.env.ref('stock.stock_location_stock').id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,
                # self.env.ref('stock.picking_type_internal').id,
            })
            move_line_id = self.env['stock.move.line'].create(move._prepare_move_line_vals())

            for line in move_line_id:
                line.lot_id = lots.lot_id.id
                line.lot_name = lots.lot_id.name
                line.qty_done = lots.product_qty
            picking_source_id.button_validate()

            lots.lot_id.stock_status = 'not_available'
            lots.lot_status = 'not_available'
            lots.lot_id.process_done = 'slitting'
            if self.operation == 'annealing':
                lots.lot_id.is_annealed = 'yes'

            # self.lot_id.stock_status = 'not_available'

        if self.multi_stage_line_ids:
            product = []
            for line in self.multi_stage_line_ids:
                if not line.is_scrap:
                    product.append(line)
            finished_picking = self.env['stock.picking'].create({
                'location_id': production_location.id,
                'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                'picking_type_id': dest_picking_type.id,
                'company_id': self.env.company.id,
                # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                # 'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_id': self.env.ref('stock.picking_type_internal').id,

            })
            self.finished_picking_id = finished_picking.id

            for products in product:
                move_lines_list = []
                new_move_list = []
                status_stock = ''
                i = bundle_quantity = 0
                sheet_numbers = 0

                if products.product_qty:
                    move = self.env['stock.move'].create({
                        'name': products.product_id.name,
                        'product_id': products.product_id.id,
                        'product_uom_qty': products.product_qty,
                        'product_uom': products.product_uom_id.id,
                        'picking_id': finished_picking.id,
                        # 'location_id': self.env.ref('stock.picking_type_internal').id,
                        'location_id': production_location.id,
                        'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                        # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,

                    })
                    self.finished_move_id = move.id
                lot_ids = []
                # sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
                rounding = products.product_uom_id.rounding
                qty = float_round(products.product_qty, precision_rounding=rounding)

                status_stock = 'available'

                new_lots = self.env['stock.production.lot'].with_context({'baby_lot': True}). \
                    create(
                    {'name': _('New'),
                     'product_id': products.product_id.id,
                     'company_id': self.env.company.id,
                     'sub_category_id': products.product_id.categ_id.id,
                     'category_id': products.product_id.categ_id.parent_id.id,
                     'product_qty': qty,
                     'weight_lb': products.product_qty,
                     'product_uom_id': products.product_uom_id.id,
                     'thickness_in': products.thickness_in,
                     'width_in': products.width_in,
                     'length_in': products.length_in if products.material_type == 'sheets' else 0,
                     'material_type': products.material_type,
                     'number_of_sheets': products.number_of_sheets if products.material_type == 'sheets' else 0,
                     'is_child_coil': True,
                     'parent_coil_id': products.lot_id.id,
                     'stock_status': status_stock,
                     'bill_of_lading': products.lot_id.bill_of_lading,
                     'vendor_id': products.lot_id.vendor_id.id if products.lot_id.vendor_id else False,
                     # 'vendor_location_id': products.lot_id.vendor_location_id.id if products.lot_id.vendor_location_id else False,
                     'vendor_serial_number': products.lot_id.vendor_serial_number,
                     'thickness_spec': products.lot_id.thickness_spec,
                     'rockwell': products.lot_id.rockwell,
                     'yield_mpa': products.lot_id.yield_mpa,
                     'elongation': products.lot_id.elongation,
                     'tensile_mpa': products.lot_id.tensile_mpa,
                     'date_received': products.lot_id.date_received,

                     'internet_serial': products.lot_id.internet_serial,
                     'packing_slip_no': products.lot_id.packing_slip_no,
                     'comp_c': products.lot_id.comp_c,
                     'comp_mn': products.lot_id.comp_mn,
                     'comp_p': products.lot_id.comp_p,
                     'comp_s': products.lot_id.comp_s,
                     'comp_si': products.lot_id.comp_si,
                     'comp_al': products.lot_id.comp_al,
                     'comp_cr': products.lot_id.comp_cr,
                     'comp_nb': products.lot_id.comp_nb,
                     'comp_ti': products.lot_id.comp_ti,
                     'comp_ca': products.lot_id.comp_ca,
                     'comp_n': products.lot_id.comp_n,
                     'comp_ni': products.lot_id.comp_ni,
                     'comp_cu': products.lot_id.comp_cu,
                     'comp_v': products.lot_id.comp_v,
                     'comp_b': products.lot_id.comp_b,
                     'pass_oil': products.lot_id.pass_oil,
                     'finish': products.lot_id.finish,
                     'temper': products.lot_id.temper,
                     'category': products.lot_id.category,
                     'coating': products.lot_id.coating,
                     'heat_number': products.lot_id.heat_number,
                     'lift_number': products.lot_id.lift_number,
                     'part_number': products.lot_id.part_number,
                     'tag_number': products.lot_id.tag_number,
                     'grade': products.lot_id.grade,
                     'quality': products.lot_id.quality,
                     'loc_city': self.dest_warehouse_id.lot_stock_id.id,
                     'loc_warehouse': self.dest_warehouse_id.id,
                     # 'loc_city': self.env.ref('stock.stock_location_stock').id,
                     # 'loc_warehouse': dest_wh.id,
                     'po_number': products.lot_id.po_number,
                     'is_annealed': 'yes' if self.operation == 'annealing' else 'no',
                     'purchase_cost': products.lot_id.purchase_cost + products.lot_id.landed_cost,
                     'total_purcahse_cost': (products.lot_id.purchase_cost + products.lot_id.landed_cost) * qty,

                     })
                new_lots._onchange_width()
                new_lots._onchange_thickness()
                new_lots._onchange_length()
                lot_ids.append(new_lots)
                products.finished_lot_id = new_lots.id
                products.lot_status = new_lots.stock_status
                move_line_id = self.env['stock.move.line'].create(
                    move._prepare_move_line_vals())

                for line in move_line_id:
                    line.lot_id = new_lots.id
                    line.qty_done = qty
                    new_move_list = line.id
            try:
                finished_picking.action_confirm()
            except:
                pass
            finished_picking.with_context({'baby_lot': True}).button_validate()
            # self.write({'state': 'done'})
            # self.lot_status = 'not_available'
            # if self.sale_order_id:
            #     print('fg')
            #     return self.action_create_picking()

    def create_picking(self):
        # line_weight = sum(self.mapped('production_line_ids').mapped('product_qty'))
        # if line_weight > self.product_qty:
        #     raise UserError(_("Sum of the Weights exceeded the Coil Weight"))
        # else:
        # lot_stock_quants = self.env['stock.quant'].search([
        #     ('lot_id', '=', self.lot_id.id)])
        # for rec in lot_stock_quants:
        #     print(rec.location_id.name, 'loccccccc')

        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id)])
        production_location = location = self.env['stock.location'].search([('usage', '=', 'production'),
                                                                            ('company_id', '=',
                                                                             self.env.company.id)],
                                                                           limit=1)
        dest_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
             ('warehouse_id', '=', self.dest_warehouse_id.id)])

        dest_wh_location = self.env.ref('stock.stock_location_stock').id
        dest_wh = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_wh_location)])

        for lots in self.pro_multi_lot_line_ids:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
                 ('warehouse_id', '=', lots.src_warehouse_id.id)])

            picking_source_id = self.env['stock.picking'].create({
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,

            })
            # self.picking_id = picking_source_id
            move = self.env['stock.move'].create({
                'name': lots.product_id.name,
                'product_id': lots.product_id.id,
                'product_uom_qty': lots.product_qty,
                'product_uom': lots.product_uom_id.id,
                'picking_id': picking_source_id.id,
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                # 'location_id': self.env.ref('stock.stock_location_stock').id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,
                # self.env.ref('stock.picking_type_internal').id,
            })
            move_line_id = self.env['stock.move.line'].create(move._prepare_move_line_vals())

            for line in move_line_id:
                line.lot_id = lots.lot_id.id
                line.lot_name = lots.lot_id.name
                line.qty_done = lots.product_qty
            picking_source_id.button_validate()

            lots.lot_id.stock_status = 'not_available'
            lots.lot_status = 'not_available'
            lots.lot_id.process_done = self.operation
            if self.operation == 'annealing':
                lots.lot_id.is_annealed = 'yes'

            # self.lot_id.stock_status = 'not_available'

        if self.production_line_ids:
            product = []
            for line in self.production_line_ids:
                if not line.is_scrap:
                    product.append(line)
            finished_picking = self.env['stock.picking'].create({
                'location_id': production_location.id,
                'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                'picking_type_id': dest_picking_type.id,
                'company_id': self.env.company.id,
                # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                # 'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_id': self.env.ref('stock.picking_type_internal').id,

            })
            self.finished_picking_id = finished_picking.id

            for products in product:
                move_lines_list = []
                new_move_list = []
                status_stock = ''
                i = bundle_quantity = 0
                sheet_numbers = 0

                if products.product_qty:
                    move = self.env['stock.move'].create({
                        'name': products.product_id.name,
                        'product_id': products.product_id.id,
                        'product_uom_qty': products.product_qty,
                        'product_uom': products.product_uom_id.id,
                        'picking_id': finished_picking.id,
                        # 'location_id': self.env.ref('stock.picking_type_internal').id,
                        'location_id': production_location.id,
                        'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                        # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,

                    })
                    self.finished_move_id = move.id
                lot_ids = []

                # sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
                rounding = products.product_uom_id.rounding
                qty = float_round(products.product_qty, precision_rounding=rounding)
                if products.production_ref_id.sale_order_id:
                    if products.is_balance == False:
                        status_stock = 'reserved'
                    else:
                        status_stock = 'available'
                else:
                    status_stock = 'available'

                new_lots = self.env['stock.production.lot'].with_context({'baby_lot': True}). \
                    create(
                    {'name': _('New'),
                     'product_id': products.product_id.id,
                     'company_id': self.env.company.id,
                     'sub_category_id': products.product_id.categ_id.id,
                     'category_id': products.product_id.categ_id.parent_id.id,
                     'product_qty': qty,
                     'weight_lb': products.product_qty,
                     'product_uom_id': products.product_uom_id.id,
                     'thickness_in': products.thickness_in,
                     'width_in': products.width_in,
                     'length_in': products.length_in if products.material_type == 'sheets' else 0,
                     'material_type': products.material_type,
                     'number_of_sheets': products.number_of_sheets if products.material_type == 'sheets' else 0,
                     'is_child_coil': True,
                     'parent_coil_id': products.lot_id.id,
                     'stock_status': status_stock,
                     'bill_of_lading': products.lot_id.bill_of_lading,
                     'vendor_id': products.lot_id.vendor_id.id if products.lot_id.vendor_id else False,
                     # 'vendor_location_id': products.lot_id.vendor_location_id.id if products.lot_id.vendor_location_id else False,
                     'vendor_serial_number': products.lot_id.vendor_serial_number,
                     'thickness_spec': products.lot_id.thickness_spec,
                     'rockwell': products.lot_id.rockwell,
                     'yield_mpa': products.lot_id.yield_mpa,
                     'elongation': products.lot_id.elongation,
                     'tensile_mpa': products.lot_id.tensile_mpa,
                     'date_received': products.lot_id.date_received,

                     'internet_serial': products.lot_id.internet_serial,
                     'packing_slip_no': products.lot_id.packing_slip_no,
                     'comp_c': products.lot_id.comp_c,
                     'comp_mn': products.lot_id.comp_mn,
                     'comp_p': products.lot_id.comp_p,
                     'comp_s': products.lot_id.comp_s,
                     'comp_si': products.lot_id.comp_si,
                     'comp_al': products.lot_id.comp_al,
                     'comp_cr': products.lot_id.comp_cr,
                     'comp_nb': products.lot_id.comp_nb,
                     'comp_ti': products.lot_id.comp_ti,
                     'comp_ca': products.lot_id.comp_ca,
                     'comp_n': products.lot_id.comp_n,
                     'comp_ni': products.lot_id.comp_ni,
                     'comp_cu': products.lot_id.comp_cu,
                     'comp_v': products.lot_id.comp_v,
                     'comp_b': products.lot_id.comp_b,
                     'pass_oil': products.lot_id.pass_oil,
                     'finish': products.lot_id.finish,
                     'temper': products.lot_id.temper,
                     'category': products.lot_id.category,
                     'coating': products.lot_id.coating,
                     'heat_number': products.lot_id.heat_number,
                     'lift_number': products.lot_id.lift_number,
                     'part_number': products.lot_id.part_number,
                     'tag_number': products.lot_id.tag_number,
                     'grade': products.lot_id.grade,
                     'quality': products.lot_id.quality,
                     'loc_city': self.dest_warehouse_id.lot_stock_id.id,
                     'loc_warehouse': self.dest_warehouse_id.id,
                     # 'loc_city': self.env.ref('stock.stock_location_stock').id,
                     # 'loc_warehouse': dest_wh.id,
                     'po_number': products.lot_id.po_number,
                     'is_annealed': 'yes' if self.operation == 'annealing' else 'no',
                     'purchase_cost': products.lot_id.purchase_cost + products.lot_id.landed_cost,
                     'total_purcahse_cost': (products.lot_id.purchase_cost + products.lot_id.landed_cost) * qty,

                     })
                new_lots._onchange_width()
                new_lots._onchange_thickness()
                new_lots._onchange_length()
                lot_ids.append(new_lots)
                products.finished_lot_id = new_lots.id
                products.lot_status = new_lots.stock_status
                move_line_id = self.env['stock.move.line'].create(
                    move._prepare_move_line_vals())

                for line in move_line_id:
                    line.lot_id = new_lots.id
                    line.qty_done = qty
                    new_move_list = line.id

            try:
                finished_picking.action_confirm()
            except:
                pass
            finished_picking.with_context({'baby_lot': True}).button_validate()
            self.write({'state': 'done'})
            # self.lot_status = 'not_available'
            if self.sale_order_id:
                print('fg')
                return self.action_create_picking()

    def action_view_stock_pickings(self):
        picking_id_list = []
        # if self.picking_id:
        #     production_picking = self.env['stock.picking'].search([('id', '=', self.picking_id.id)])
        #     picking_id_list.append(production_picking.id)
        if self.finished_picking_id:
            finished_picking = self.env['stock.picking'].search([('id', '=', self.finished_picking_id.id)])
            picking_id_list.append(finished_picking.id)
        # if picking_id_list:
        #     self.is_picking = True
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

    def action_view_delivery(self):
        if self.sale_order_id:
            deliveries = self.sale_order_id.mapped('picking_ids')

            if deliveries:
                return {
                    'name': _('Delivery'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'stock.picking',
                    'view_id': False,
                    'domain': [('id', 'in', deliveries.ids)],

                }

    def action_create_picking(self):
        supplierloc = self.env['stock.warehouse']._get_partner_locations()
        for pick in self.sale_order_id.picking_ids:
            if pick:
                for move in pick.move_lines:
                    if move.sale_line_id.id == self.sale_line_id.id:

                        move.with_context(prefetch_fields=False, production_lot=True).mapped('move_line_ids').unlink()
                        move_line_id = self.env['stock.move.line'].with_context({'production_lot': True}).create(
                            move._prepare_move_line_vals())

                        for lines in move_line_id:
                            lines.product_id = self.sale_line_id.product_id.id
                            lines.product_uom_qty = self.sale_line_id.product_uom_qty
                            lines.location_id = self.dest_warehouse_id.lot_stock_id.id,
                            # lines.location_id = self.env.ref('stock.stock_location_stock').id
                            # lines.state = 'assigned'

                        pick.write({'sale_id': self.sale_order_id.id,
                                    'is_jo_picking': True})
                        pick.with_context({'production_lot': True}).action_confirm()
                        pick.with_context({'production_lot': True}).action_assign()


class SteelProductionLine(models.Model):
    _name = 'steel.production.line'
    _description = 'Steel Production'

    @api.onchange('sale_order_ref')
    def _domain_sale_order_line(self):
        if self.sale_order_ref:
            return {'domain': {'sale_order_line_ref': [('order_id', '=', self.sale_order_ref.id)]}}
        else:
            return {'domain': {'sale_order_line_ref': [()]}}

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Source", track_visibility='onchange')
    finished_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="New Lot Number",
                                      track_visibility='onchange')
    bundle_lot_ids = fields.Many2many(comodel_name='stock.production.lot', string="New Lot Nos.",
                                      track_visibility='onchange')
    is_balance = fields.Boolean(string='Is Balance', default=False, copy=False)
    is_scrap = fields.Boolean(string='Is scrap', default=False, copy=False)
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')
    # domain=[('is_source_lot', '=', True)])

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Sub Product')
    product_qty = fields.Float(string='Weight')
    # , compute='compute_product_weight'
    width_in = fields.Float(string='Width(in)', digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    number_of_sheets = fields.Float(string='Sheets')
    length_in = fields.Float(string='Length(in)', digits=[8, 4])
    bundles = fields.Integer(string='Bundles')
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    production_ref_id = fields.Many2one('steel.production', string='Production Ref')
    lot_status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('not_available', 'Not available')
    ], string='Stock Status', default='in_production', track_visibility="onchange")
    is_update_lot_in_stock = fields.Boolean('Update Stock', default=False)
    # is_lot_updated_to_so = fields.Boolean('Update SO', default=False)

    sale_order_ref = fields.Many2one('sale.order', string="Sale Orders", domain="[('state', '=', 'draft') or [] ] ")
    sale_order_line_ref = fields.Many2one('sale.order.line', string="Order Line",
                                          domain="[('order_id', '=', sale_order_ref) or [] ] ")

    def attach_lots_to_sale_order(self):
        if self.finished_lot_id and self.sale_order_ref and self.sale_order_line_ref:
            if self.sale_order_ref.warehouse_id == self.production_ref_id.dest_warehouse_id:
                if self.sub_category_id == self.sale_order_line_ref.sub_category_id and self.product_id == self.sale_order_line_ref.product_id:
                    if self.thickness_in == self.sale_order_line_ref.thickness_in and self.width_in == self.sale_order_line_ref.width_in:
                        self.sale_order_line_ref.write({
                            'lot_id': self.finished_lot_id.id,
                            'product_uom_qty': self.product_qty,
                            'product_uom': self.product_uom_id.id,
                            'width_in': self.finished_lot_id.width_in,
                            'length_in': self.finished_lot_id.length_in,
                            'material_type': self.finished_lot_id.material_type,
                        })
                        # self.is_lot_updated_to_so = True
                        return {
                            'name': _('Sale Order Attachment'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'production.sale.attach.wizard',
                            'views': [(False, 'form')],
                            'view_id': False,
                            'target': 'new',
                            # 'context': {
                            #     'default_production_id': self.production_ref_id.id,
                            # }
                        }

                    else:
                        raise UserError(
                            _("Thickness/Width of the selected sale order line is different"))
                else:
                    raise UserError(
                        _("Product Specs are different"))
            else:
                raise UserError(
                    _("Warehouse of the selected sale order must be same as the destination Warehouse"))

    # lot_status = fields.Selection(string='Status', related='finished_lot_id.stock_status', track_visibility="onchange")

    def update_lot_in_stock(self):
        if self.production_ref_id:
            if self.production_ref_id.sale_line_id:
                if not self.is_balance:
                    if self.finished_lot_id:
                        self.is_update_lot_in_stock = True
                        self.production_ref_id.sale_line_id.write({'produced_lot_ids': [(4, self.finished_lot_id.id)]})
                        # self.sale_line_id.lot_id = new_lots.id
                        move_lines_id = self.env['stock.move'].search(
                            [('sale_line_id', '=', self.production_ref_id.sale_line_id.id)])
                        if move_lines_id:
                            if move_lines_id.move_line_ids:
                                if len(move_lines_id.move_line_ids) == 1:
                                    if move_lines_id.move_line_ids.lot_id:
                                        if move_lines_id.move_line_ids.lot_id != self.finished_lot_id:
                                            move_line_id = self.env['stock.move.line'].with_context(
                                                {'production_lot': True}).create(
                                                move_lines_id._prepare_move_line_vals())
                                            move_line_id.with_context({'production_lot': True}).write(
                                                {'lot_id': self.finished_lot_id.id,
                                                 'product_uom_qty': self.product_qty})
                                    else:
                                        move_lines_id.move_line_ids.with_context({'production_lot': True}).write(
                                            {'lot_id': self.finished_lot_id.id,
                                             'product_uom_qty': self.product_qty})
                                else:
                                    no_move = False
                                    for line in move_lines_id.move_line_ids:
                                        if line.lot_id != self.finished_lot_id:
                                            no_move = True
                                    if no_move:
                                        move_line_id = self.env['stock.move.line'].with_context(
                                            {'production_lot': True}).create(
                                            move_lines_id._prepare_move_line_vals())
                                        move_line_id.with_context({'production_lot': True}).write(
                                            {'lot_id': self.finished_lot_id.id,
                                             'product_uom_qty': self.product_qty})

                    # else:
                    #     if self.bundle_lot_ids:
                    #         lot_list = []
                    #         for bundle_lot in self.bundle_lot_ids:
                    #             lot_list.append(bundle_lot.id)
                    #
                    #         self.is_update_lot_in_stock = True
                    #         self.production_ref_id.sale_line_id.write(
                    #             {'produced_lot_ids': [(4, lot.id) for lot in self.bundle_lot_ids]})
                    #
                    #         move_lines_id = self.env['stock.move'].search(
                    #             [('sale_line_id', '=', self.production_ref_id.sale_line_id.id)])
                    #         if move_lines_id:
                    #             if move_lines_id.move_line_ids:
                    #                 if len(move_lines_id.move_line_ids) == 1:
                    #                     if move_lines_id.move_line_ids.lot_id:
                    #                         for lot in lot_list:
                    #                             if move_lines_id.move_line_ids.lot_id != lot:
                    #                                 move_line_id = self.env['stock.move.line'].create(
                    #                                     move_lines_id._prepare_move_line_vals())
                    #                                 move_line_id.write({'lot_id': lot,
                    #                                                     'product_uom_qty': int(
                    #                                                         self.product_qty / self.bundles)})
                    #                     else:
                    #                         move_lines_id.move_line_ids.write({'lot_id': lot_list[0],
                    #                                                            'product_uom_qty': int(
                    #                                                                self.product_qty / self.bundles)})
                    #                         lot_list.pop(0)
                    #                         for rec in lot_list:
                    #                             move_line_id = self.env['stock.move.line'].create(
                    #                                 move_lines_id._prepare_move_line_vals())
                    #                             move_line_id.write({'lot_id': rec,
                    #                                                 'product_uom_qty': int(
                    #                                                     self.product_qty / self.bundles)})
                    #                 else:
                    #                     no_move = False
                    #                     for line in move_lines_id.move_line_ids:
                    #                         for rec in self.bundle_lot_ids:
                    #                             if line.lot_id != rec.id:
                    #                                 no_move = True
                    #                     if no_move:
                    #                         for val in lot_list:
                    #                             move_line_id = self.env['stock.move.line'].create(
                    #                                 move_lines_id._prepare_move_line_vals())
                    #                             move_line_id.write({'lot_id': val,
                    #                                                 'product_uom_qty': int(
                    #                                                     self.product_qty / self.bundles)})

    @api.onchange('width_in', 'material_type')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in and self.material_type == 'coil':
            for rec in self.production_ref_id.pro_multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_weight = rec.product_qty
                    coil_width = rec.width_in

            if self.production_ref_id.operation == 'slitting' or self.production_ref_id.operation == 'parting':
                unit_weight = int(coil_weight / coil_width)
                self.product_qty = int(unit_weight * self.width_in)

            if self.production_ref_id.operation == 'multistage':
                if self.production_ref_id.second_operation == 'parting':
                    unit_weight = int(coil_weight / coil_width)
                    self.product_qty = int(unit_weight * self.width_in)

    @api.onchange('width_in', 'length_in', 'number_of_sheets')
    def _onchange_sheets(self):
        if self.material_type == 'sheets':

            coil_thickness = unit_sheet_weight = 0
            for rec in self.production_ref_id.pro_multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_thickness = rec.thickness_in
                    coil_width = rec.width_in
            # coil_thickness = self.job_ref_id.thickness_in
            unit_sheet_weight = int(coil_thickness * self.width_in * self.length_in * 0.284)
            self.product_qty = int(unit_sheet_weight * self.number_of_sheets)

    def get_finished_lot_barcode(self):
        return self.env.ref('odx_steel_production.barcode_for_finished_lot').report_action(self)


class MultiStageLine(models.Model):
    _name = 'multi.stage.line'
    _description = 'Steel Production'

    @api.onchange('width_in', 'material_type')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in and self.material_type == 'coil':
            for rec in self.production_stage_id.pro_multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_weight = rec.product_qty
                    coil_width = rec.width_in

            if self.production_stage_id.operation == 'multistage':
                # coil_weight = self.job_stage_id.product_qty
                # coil_width = self.job_stage_id.width_in
                unit_weight = int(coil_weight / coil_width)
                self.product_qty = int(unit_weight * self.width_in)

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Source", track_visibility='onchange')
    finished_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="New Tag No",
                                      track_visibility='onchange')
    is_balance = fields.Boolean(string='Is Balance', default=False, copy=False)
    is_scrap = fields.Boolean(string='Is Scrap', default=False, copy=False)
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Sub Product')
    product_qty = fields.Float(string='Weight')
    width_in = fields.Float(string='Width(in)', digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    production_stage_id = fields.Many2one('steel.production', string='Production Ref')
    remarks = fields.Selection([
        ('restock', 'Restock'),
        ('run2', 'Send for 2nd run'),
        ('scrap', 'Scrap Wt')
    ], string='Remarks')

    def action_production_order_line(self):
        production_lines = []
        if self.finished_lot_id:
            self.production_stage_id.second_run_lot_id = self.finished_lot_id.id

            for line in self:
                production_lines.append((0, 0, {
                    'lot_id': line.finished_lot_id.id,
                    'product_id': line.finished_lot_id.product_id.id,
                    'category_id': line.finished_lot_id.category_id.id,
                    'sub_category_id': line.finished_lot_id.sub_category_id.id,
                    'product_uom_id': line.finished_lot_id.product_uom_id.id,
                    'thickness_in': line.thickness_in,
                    'product_qty': line.product_qty,
                    'width_in': line.width_in,
                    # 'remarks': line.remarks,
                    # 'is_scrap': line.is_scrap,
                    # 'material_type': 'coil',
                    # 'src_warehouse_id': self.lot_id.loc_warehouse.id,

                }))
            action = {
                'type': 'ir.actions.act_window',
                'views': [(self.env.ref('odx_steel_production.second_run_wizard_view').id, 'form')],
                'view_mode': 'form',
                'context': {'default_line_order_ids': production_lines,
                            'default_multi_stage_id': self.id,
                            'default_production_id': self.production_stage_id.id,
                            'default_source_lot_id': self.finished_lot_id.id
                            },
                'target': 'new',
                'name': _('Second Run'),
                'res_model': 'second.run.wizard', }
            return action
        else:
            raise UserError(_('Please click create picking and generate lot.'))

    # number_of_sheets = fields.Float(string='Sheets')
    # length_in = fields.Float(string='Length(in)', digits=[8, 4])
    # lot_status = fields.Selection([
    #     ('available', 'Available'),
    #     ('reserved', 'Reserved'),
    #     ('in_production', 'In production'),
    #     ('not_available', 'Not available')
    # ], string='Stock Status', default='in_production', track_visibility="onchange")
    # is_update_lot_in_stock = fields.Boolean('Update Stock', default=False)
