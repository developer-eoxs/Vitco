from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.tools import float_round


class JobOrder(models.Model):
    _name = 'job.order'
    _description = 'Job Order'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('job.order.sequence') or _('New')
        return super(JobOrder, self).create(vals)

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
        self.src_warehouse_id = self.lot_id.loc_warehouse.id
        self.dest_warehouse_id = self.lot_id.loc_warehouse.id

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

    def action_confirm(self):
        for line in self.job_line_ids:
            if line.product_qty <= 0:
                raise UserError(
                    _("Weight is not Provided in line"))
        if not self.sale_order_id:
            for lot in self.multi_lot_line_ids:
                lot.lot_id.stock_status = 'in_production'
                lot.lot_status = 'in_production'

        for tags in self.multi_lot_line_ids:
            line_width = line_weight = residue_width = residue_weight = multi_stage_width = multi_stage_weight = 0
            multistage_residue_width = multistage_residue_wt = 0
            for lines in self.job_line_ids:
                if tags.lot_id == lines.lot_id:
                    line_width += lines.width_in
                    line_weight += lines.product_qty
                    # line_width = sum(self.mapped('job_line_ids').mapped('width_in'))
                    # line_weight = sum(self.mapped('job_line_ids').mapped('product_qty'))

            if self.operation == 'multistage':
                for stage_lines in self.multi_stage_line_ids:
                    if tags.lot_id == stage_lines.lot_id:
                        multi_stage_width += stage_lines.width_in
                        multi_stage_weight += stage_lines.product_qty
                        # multi_stage_weight += sum(self.mapped('multi_stage_line_ids').mapped('product_qty'))

            residue_width = tags.width_in - line_width
            residue_weight = tags.product_qty - line_weight
            print(residue_weight, 'wtt')
            multistage_residue_width = tags.width_in - multi_stage_width
            multistage_residue_wt = tags.product_qty - multi_stage_weight

            if self.operation == 'slitting' or self.operation == 'annealing':
                # if (line_width <= tags.width_in) and (line_weight <= tags.product_qty):
                if (line_width <= tags.width_in):
                    if (line_weight <= tags.product_qty):
                        if line_width < tags.width_in or line_weight < tags.product_qty:
                            self.write({
                                'job_line_ids': [(0, 0, {
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
                            self.write({'state': 'confirm'})
                    else:
                        raise UserError(_("Sum of the weights exceeded the Coil weight"))
                        # self.write({'state': 'confirm'})
                else:
                    raise UserError(_("Sum of the widths exceeded the Coil Width"))

            elif self.operation == 'multistage':

                for multi_line in self.multi_stage_line_ids:
                    if multi_line.lot_id == tags.lot_id:
                        self.write({
                            'job_line_ids': [(0, 0, {
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
                            'job_line_ids': [(0, 0, {
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
                            'job_line_ids': [(0, 0, {
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
                width_balance = 0
                if self.operation == 'cutting':
                    width_balance = tags.width_in
                else:
                    width_balance = residue_width

                if line_weight <= tags.product_qty:
                    if line_weight < tags.product_qty:
                        self.write({
                            'job_line_ids': [(0, 0, {
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

    def add_line(self):
        for tags in self.multi_lot_line_ids:
            if self.second_operation == 'parting' and tags.number_of_parts > 0:
                i = 0
                while i < tags.number_of_parts:
                    self.write({
                        'job_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
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
                        'job_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': self.order_line_product.id if self.order_line_product else tags.product_id.id,
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

    def action_cancel(self):
        if self.user_has_groups('odx_steel_production.group_steel_production_manager'):
            return {
                'name': _('Cancel Job Order'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'job.order.cancel.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_job_order_id': self.id,
                }
            }

        else:
            raise UserError(_('You do not have the permission to Cancel.Please Contact Administrator.'))

    def action_reset_to_draft(self):
        if self.state == 'confirm':
            self.write({
                'state': 'draft'
            })
            self.job_line_ids = False
            for rec in self.multi_lot_line_ids:
                rec.lot_id.stock_status = 'available'
                rec.lot_status = 'available'

    name = fields.Char(
        'Reference', default=lambda self: _('New'),
        required=True, readonly=True, copy=False, help="Reference")
    # default=lambda self: self.env['ir.sequence'].next_by_code('job.order.sequence'),

    src_warehouse_id = fields.Many2one('stock.warehouse', 'Source Warehouse',
                                       )
    dest_warehouse_id = fields.Many2one('stock.warehouse', 'Dest. Warehouse',
                                        required=True)

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
        ('multistage', 'MultiStage'),
        ('annealing', 'Annealing'),
        ('cr', 'Cold Rolling'),
        ('degreasing', 'DeGreasing'),
        ('tr', 'Temper Rolling'),
        ('pickling', 'Pickling'),
    ], string='Operation', required=True, default='slitting', track_visibility="onchange")

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
                             domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available'), ])
    # ('loc_warehouse', '=', 'src_warehouse_id')
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
    job_line_ids = fields.One2many('job.order.line', 'job_ref_id', string="Job Line")
    job_event_date = fields.Datetime(string="Job Event Date")
    job_processed_date = fields.Datetime(string="Job Processed Date")
    job_due_date = fields.Date(string="Due Date")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,
                                 default=lambda self: self.env.user.company_id)
    multi_stage_line_ids = fields.One2many('job.multi.stage.line', 'job_stage_id', string="Multi Stage Line")
    multi_lot_line_ids = fields.One2many('multi.lot.line', 'job_order_ref_id', string="Multi lot Line")

    shipped_via = fields.Char(string="Shipped Via")
    payment_terms = fields.Char(string="Payment Terms")
    fob_point = fields.Char(string="F.O.B Point")
    technical_delivery_cond = fields.Html(string="Technical Delivery Conditions", translate=True,
                                          default=_get_default_ftechnical_delivery_cond)
    terms_conditions = fields.Html(string='Terms & Conditions', translate=True, default=_get_default_terms)

    coil_processing_details = fields.Html(string="Coil Processing Details", translate=True)
    order_line_product = fields.Many2one('product.product', string='OrderLine Product')

    def create_picking(self):
        # line_weight = sum(self.mapped('job_line_ids').mapped('product_qty'))
        # if line_weight > self.product_qty:
        #     raise UserError(_("Sum of the Weights exceeded the Coil Weight"))
        # else:

        dest_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
             ('warehouse_id', '=', self.dest_warehouse_id.id)])
        production_location = location = self.env['stock.location'].search([('usage', '=', 'production'),
                                                                            ('company_id', '=',
                                                                             self.env.company.id)],
                                                                           limit=1)
        for lots in self.multi_lot_line_ids:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
                 ('warehouse_id', '=', lots.src_warehouse_id.id)])

            picking_source_id = self.env['stock.picking'].create({
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
                # 'partner_id': self.source_id.partner_id.id,
                # 'location_id': self.env.ref('stock.stock_location_stock').id,
                # 'location_dest_id': self.env.ref('stock.picking_type_internal').id,

            })
            # self.picking_id = picking_source_id
            print(picking_source_id, "picking_source_id")
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

        if self.job_line_ids:
            product = []
            for line in self.job_line_ids:
                if not line.is_scrap:
                    product.append(line)
            print(product)
            finished_picking = self.env['stock.picking'].create({
                'location_id': production_location.id,
                'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                'picking_type_id': dest_picking_type.id,
                'company_id': self.env.company.id,
                # 'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                # 'location_dest_id': self.env.ref('stock.stock_location_stock').id,

            })
            self.finished_picking_id = finished_picking.id
            print(self.finished_picking_id, "self.finished_picking_id")
            for products in product:
                move_lines_list = []
                new_move_list = []
                status_stock = ''

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
                if products.job_ref_id.sale_order_id:
                    if products.is_balance == False:
                        status_stock = 'reserved'
                    else:
                        status_stock = 'available'
                else:
                    status_stock = 'available'

                # if self.operation=='annealing' or self.lot_id:
                #     annealed='yes'
                #

                # if products.material_type == 'sheets' and products.bundle>1
                #     'reserved' if products.is_balance == False else 'available',
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
                     'vendor_id': self.partner_id.id if self.partner_id else False,
                     # 'vendor_location_id': self.vendor_id.vendor_location_id.id if self.lot_id.vendor_location_id else False,
                     'vendor_serial_number': self.partner_id.vendor_serial_number if self.partner_id.vendor_serial_number else '',
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
                     'heat_number': products.lot_id.heat_number_pr1 if products.lot_id.heat_number_pr1 else products.lot_id.heat_number,
                     'lift_number': products.lot_id.lift_number_pr1 if products.lot_id.lift_number_pr1 else products.lot_id.lift_number,
                     'part_number': products.lot_id.part_number_pr1 if products.lot_id.part_number_pr1 else products.lot_id.part_number,
                     'tag_number': products.lot_id.tag_number_pr1 if products.lot_id.tag_number_pr1 else products.lot_id.tag_number,
                     'job_order_lot': True,
                     'loc_city': self.dest_warehouse_id.lot_stock_id.id,
                     'loc_warehouse': self.dest_warehouse_id.id,
                     'po_number': products.lot_id.po_number,
                     'grade': products.lot_id.grade,
                     'quality': products.lot_id.quality,
                     # 'process_done': self.operation,
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
            self.job_processed_date = fields.Datetime.now()
            if self.sale_order_id:
                print('fg')
                return self.action_create_picking()

    def generate_freight(self):
        freight_object = self.env['freight.management']
        new_freight = freight_object.create({
            'job_order_id': self.id
        })
        for line in self.job_line_ids:
            new_freight.write({
                'cargo_lines': [(0, 0, {
                    'name': line.product_id.name,
                    'product_uom_qty': line.product_qty,
                    'product_id': line.product_id.id if line.product_id else False,
                    'lot_ids': [(4, line.finished_lot_id.id)] if line.finished_lot_id else False,
                })]
            })

        return {
            'name': 'Freight Management',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'freight.management',
            'view_id': False,
            'target': 'current',
            'res_id': new_freight.id,
            'type': 'ir.actions.act_window',
        }

    def action_view_freight(self):
        job_id_list = []
        freight_picking = self.env['freight.management'].search([('job_order_id', '=', self.id)])
        if freight_picking:
            for rec in freight_picking:
                job_id_list.append(rec.id)
        if job_id_list:
            return {
                'name': 'Freight Management',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'freight.management',
                'view_id': False,
                'target': 'current',
                'domain': [('id', '=', job_id_list)],
                'type': 'ir.actions.act_window',
            }
        else:
            raise UserError(_('No freights are assigned.'))

    def send_job_order(self):
        self.ensure_one()
        # for line in self:
        template_id = self.env.ref('odx_steel_production.mail_template_job_order_eoxs').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'job.order', self.ids[0])
        ctx = {
            'default_model': 'job.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'custom_layout': "mail.mail_notification_paynow",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'active_ids': self.ids,
            'model_description': self.with_context(lang=lang).name,
        }
        return {
            'name': _('Send Job Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def add_scrap_line(self):
        for tags in self.multi_lot_line_ids:
            balance_wt = 0
            line_weight = 0
            for lines in self.job_line_ids:
                if tags.lot_id == lines.lot_id:
                    line_weight += lines.product_qty

            balance_wt = tags.product_qty - line_weight
            if line_weight < tags.product_qty:
                self.write({
                    'job_line_ids': [(0, 0, {
                        'lot_id': tags.lot_id.id,
                        'product_id': tags.product_id.id,
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
                            # lines.state = 'assigned'

                        pick.write({'sale_id': self.sale_order_id.id,
                                    'is_jo_picking': True})
                        pick.with_context({'production_lot': True}).action_confirm()
                        pick.with_context({'production_lot': True}).action_assign()


class JobOrderLine(models.Model):
    _name = 'job.order.line'
    _description = 'Job Order'

    @api.onchange('description')
    def _onchange_description(self):
        if not self.finished_lot_id.tag_number_pr1:
            self.finished_lot_id.tag_number_pr1 = self.description
        elif not self.finished_lot_id.tag_number_pr2:
            self.finished_lot_id.tag_number_pr2 = self.description
        elif not self.finished_lot_id.tag_number_pr3:
            self.finished_lot_id.tag_number_pr3 = self.description
        else:
            self.finished_lot_id.tag_number_pr4 = self.description

    @api.onchange('sub_category_id')
    def _domain_product_id(self):

        if self.sub_category_id:
            return {'domain': {'product_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_id': []}}

    @api.onchange('sale_order_ref')
    def _domain_sale_order_line(self):
        if self.sale_order_ref:
            return {'domain': {'sale_order_line_ref': [('order_id', '=', self.sale_order_ref.id)]}}
        else:
            return {'domain': {'sale_order_line_ref': [()]}}

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Source", track_visibility='onchange')
    finished_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="New Lot Number",
                                      track_visibility='onchange')
    is_balance = fields.Boolean(string='Is Balance', default=False, copy=False)
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')
    # domain=[('is_source_lot', '=', True)])

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    product_id = fields.Many2one('product.product', string='Sub Product',
                                 domain="[('categ_id', '=', sub_category_id) or [] ] ")
    product_qty = fields.Float(string='Weight')
    # , compute='compute_product_weight'
    width_in = fields.Float(string='Width(in)', digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    number_of_sheets = fields.Float(string='Sheets')
    length_in = fields.Float(string='Length(in)', digits=[8, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    job_ref_id = fields.Many2one('job.order', string='Job Ref')
    lot_status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('not_available', 'Not available')
    ], string='Stock Status', default='in_production', track_visibility="onchange")
    is_update_lot_in_stock = fields.Boolean('Update Stock', default=False)
    # is_lot_updated_to_so = fields.Boolean('Update SO', default=False)

    is_scrap = fields.Boolean('Is scrap', default=False)
    description = fields.Char('Processor Tags')
    pricing = fields.Float(string="Pricing")
    sale_order_ref = fields.Many2one('sale.order', string="Sale Orders", domain="[('state', '=', 'draft') or [] ] ")
    sale_order_line_ref = fields.Many2one('sale.order.line', string="Order Line",
                                          domain="[('order_id', '=', sale_order_ref) or [] ] ")

    # tag_ref_id = fields.Many2one('multi.lot.line', string="Tag Ref")

    # lot_status = fields.Selection(string='Status', related='finished_lot_id.stock_status', track_visibility="onchange")

    def update_lot_in_stock(self):
        if self.job_ref_id:
            if self.job_ref_id.sale_line_id:
                if not self.is_balance:
                    if self.finished_lot_id:
                        self.is_update_lot_in_stock = True
                        self.job_ref_id.sale_line_id.write({'produced_lot_ids': [(4, self.finished_lot_id.id)]})
                        # self.sale_line_id.lot_id = new_lots.id
                        move_lines_id = self.env['stock.move'].search(
                            [('sale_line_id', '=', self.job_ref_id.sale_line_id.id)])

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

    def attach_lots_to_sale_order(self):
        if self.finished_lot_id and self.sale_order_ref and self.sale_order_line_ref:
            if self.sale_order_ref.warehouse_id == self.job_ref_id.dest_warehouse_id:
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

    @api.onchange('width_in', 'material_type')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in and self.material_type == 'coil':
            for rec in self.job_ref_id.multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_weight = rec.product_qty
                    coil_width = rec.width_in

            if self.job_ref_id.operation == 'slitting' or self.job_ref_id.operation == 'parting':
                unit_weight = int(coil_weight / coil_width)
                self.product_qty = int(unit_weight * self.width_in)

            if self.job_ref_id.operation == 'multistage':
                if self.job_ref_id.second_operation == 'parting':
                    unit_weight = int(coil_weight / coil_width)
                    self.product_qty = int(unit_weight * self.width_in)

    @api.onchange('width_in', 'length_in', 'number_of_sheets')
    def _onchange_sheets(self):
        if self.material_type == 'sheets':

            coil_thickness = unit_sheet_weight = 0
            for rec in self.job_ref_id.multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_thickness = rec.thickness_in
                    coil_width = rec.width_in
            # coil_thickness = self.job_ref_id.thickness_in
            unit_sheet_weight = int(coil_thickness * self.width_in * self.length_in * 0.284)
            self.product_qty = int(unit_sheet_weight * self.number_of_sheets)

    def get_jo_finished_lot_barcode(self):
        return self.env.ref('odx_steel_production.barcode_for_finished_lot_jo').report_action(self)


class JobMultiStageLine(models.Model):
    _name = 'job.multi.stage.line'
    _description = 'Job Order Multi Stage Line'

    @api.onchange('width_in', 'material_type')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in and self.material_type == 'coil':
            for rec in self.job_stage_id.multi_lot_line_ids:
                if self.lot_id == rec.lot_id:
                    coil_weight = rec.product_qty
                    coil_width = rec.width_in

            if self.job_stage_id.operation == 'multistage':
                # coil_weight = self.job_stage_id.product_qty
                # coil_width = self.job_stage_id.width_in
                unit_weight = int(coil_weight / coil_width)
                self.product_qty = int(unit_weight * self.width_in)

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Source", track_visibility='onchange')
    # finished_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="New Lot",
    #                                   track_visibility='onchange')
    is_balance = fields.Boolean(string='Is Balance', default=False, copy=False)
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
    job_stage_id = fields.Many2one('job.order', string='Job Ref')
    # number_of_sheets = fields.Float(string='Sheets')
