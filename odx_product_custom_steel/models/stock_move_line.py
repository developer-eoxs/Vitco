from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft',
                                 related="lot_id.state", readonly=True)
    select = fields.Boolean(string="Select")
    is_invisible = fields.Boolean(compute='button_visibility', string="Button condition")
    # lot_id = fields.Many2one(
    #     'stock.production.lot', 'Lot/Serial Number',
    #     domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]", check_company=True)


    @api.onchange('lot_id')
    def onchange_lot_id_for_product(self):
        if self._context.get('is_internal_only'):
            # print("lot id change")
            self.product_id = self.lot_id.product_id.id
            self.qty_done = self.lot_id.product_qty

    @api.onchange('state', 'lot_id')
    def button_visibility(self):
        self.is_invisible = False
        for rec in self:
            if self._context.get('show_lots_m2o'):
                rec.is_invisible = True
            if not self._context.get('show_lots_m2o'):
                if rec.state == 'confirm' or rec.lot_id:
                    rec.is_invisible = True
                else:
                    rec.is_invisible = False

    # description = fields.Char(string="Description")

    def stock_lot_action(self):
        return {
            'name': _('Stock Production Lot'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.production.lot',
            'res_id': self.lot_id.id,
            'views': [(False, 'form')],
            'view_id': 'stock.view_production_lot_form',
            'target': 'new',
            # 'context': ctx,
        }

    def get_lot_serial(self):
        # for line in self.move_line_nosuggest_ids:
        if not self.lot_id:
            if self.qty_done > 0:
                sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
                wt_kg = (self.qty_done * 0.453592)
                lot_a = self.env['stock.production.lot']. \
                    create(
                    {'name': str(sequence),
                     'product_id': self.product_id.id,
                     'company_id': self.env.company.id,
                     'product_qty': self.qty_done,
                     'weight_kg': wt_kg,
                     'weight_lb': self.qty_done,
                     'sub_category_id': self.product_id.categ_id.id,
                     'category_id': self.product_id.categ_id.parent_id.id,
                     'product_template_id': self.product_id.product_tmpl_id.id,
                     'po_number': self.origin,
                     'vendor_serial_number': self.mapped('picking_id').mapped('partner_id').vendor_serial_number or '',
                     'vendor_id': self.mapped('picking_id').mapped('partner_id').id or False,
                     'loc_city': self.mapped('picking_id').mapped('picking_type_id').mapped(
                         'default_location_dest_id').id or False,
                     'loc_warehouse': self.mapped('picking_id').mapped('picking_type_id').mapped(
                         'warehouse_id').id or False,
                     'material_type': 'sheets' if self.move_id.length_in > 0 else 'coil',
                     'stock_status': 'transit',
                     'width_in': self.move_id.width_in,
                     'thickness_in': self.move_id.thickness_in,
                     'length_in': self.move_id.length_in,
                     'heat_number': self.move_id.offer_id.heat_number if self.move_id.offer_id.heat_number else '',
                     'tag_number': self.move_id.offer_id.batch if self.move_id.offer_id.batch else '',
                     'comp_c': self.move_id.offer_id.comp_c,
                     'comp_mn': self.move_id.offer_id.comp_mn,
                     'comp_p': self.move_id.offer_id.comp_p,
                     'comp_s': self.move_id.offer_id.comp_s,
                     'comp_si': self.move_id.offer_id.comp_si,
                     'comp_al': self.move_id.offer_id.comp_al,

                     'comp_ti': self.move_id.offer_id.comp_ti,
                     'comp_nb': self.move_id.offer_id.comp_nb,
                     'comp_b': self.move_id.offer_id.comp_b,
                     'comp_cu': self.move_id.offer_id.comp_cu,
                     'comp_co': self.move_id.offer_id.comp_co,
                     'comp_cr': self.move_id.offer_id.comp_cr,
                     'comp_mo': self.move_id.offer_id.comp_mo,
                     'comp_n': self.move_id.offer_id.comp_n,
                     'comp_ni': self.move_id.offer_id.comp_ni,
                     'comp_v': self.move_id.offer_id.comp_v,
                     # 'comp_pb': self.move_id.offer_id.comp_pb,
                     # 'comp_as': self.move_id.offer_id.comp_as,
                     # 'packing_slip_no': self.picking_id.packing_slip_no or '',
                     # 'bill_of_lading': self.picking_id.bill_of_lading or '',
                     #  # 'date_received': self.mapped('picking_id').date_received or False,
                     # 'vendor_location_id': self.mapped('picking_id').mapped('vendor_location_id').id or False,
                     })
                lot_a._onchange_thickness()
                lot_a._onchange_width()
                lot_a._onchange_length()
                self.lot_id = lot_a.id
                self.lot_name = lot_a.name
            else:
                raise UserError(_('Please provide the quantity.'))
        else:
            raise UserError(_('Lot is already generated for this quantity.'))

        return {
            'name': _('Stock Production Lot'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.production.lot',
            'res_id': self.lot_id.id,
            'views': [(False, 'form')],
            'view_id': 'stock.view_production_lot_form',
            'target': 'new',
            # 'context': {

            # }
        }

    def _action_done(self):

        for ml in self:

            if ml.picking_id.picking_type_id.code == 'internal':
                if ml.lot_id:
                    lot = ml.lot_id
                    if ml.picking_id:
                        if ml.picking_id.location_dest_id:
                            wh = self.env['stock.warehouse'].search(
                                [('lot_stock_id', '=', ml.picking_id.location_dest_id.id)],
                                limit=1)
                            lot.loc_city = ml.picking_id.location_dest_id.id or False
                            lot.loc_warehouse = wh.id

        return super(StockMoveLine, self)._action_done()


class StockMove(models.Model):
    _inherit = 'stock.move'

    description = fields.Char(string='Description', related='product_id.name')
    offer_id = fields.Many2one('purchase.offer', string='Offers')
    is_select = fields.Boolean(string="Is Select", compute='_onchange_move_line')
    lot_id = fields.Many2one('stock.production.lot', string="Lots")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", related='product_id.categ_id')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])

    @api.depends('move_line_nosuggest_ids.select')
    def _onchange_move_line(self):
        self.is_select = False
        for line in self.move_line_nosuggest_ids:
            if line.select and not line.lot_id:
                self.is_select = True

    def select_all_lines(self):
        for line in self.move_line_nosuggest_ids:
            line.select = True

    def un_select_all_lines(self):
        for line in self.move_line_nosuggest_ids:
            line.select = False

    def gen_lot_serial(self):
        for line in self.move_line_nosuggest_ids:
            if not line.lot_id and line.select:
                if line.qty_done > 0:
                    sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
                    wt_kg = (line.qty_done * 0.453592)
                    lot_a = self.env['stock.production.lot']. \
                        create(
                        {'name': str(sequence),
                         'product_id': line.product_id.id,
                         'company_id': line.env.company.id,
                         'product_qty': line.qty_done,
                         'weight_kg': wt_kg,
                         'weight_lb': line.qty_done,
                         'sub_category_id': line.product_id.categ_id.id,
                         'category_id': line.product_id.categ_id.parent_id.id,
                         'product_template_id': line.product_id.product_tmpl_id.id,
                         'po_number': line.origin,
                         'vendor_serial_number': line.mapped('picking_id').mapped(
                             'partner_id').vendor_serial_number or '',
                         'vendor_id': line.mapped('picking_id').mapped('partner_id').id or False,
                         'loc_city': line.mapped('picking_id').mapped('picking_type_id').mapped(
                             'default_location_dest_id').id or False,
                         'loc_warehouse': line.mapped('picking_id').mapped('picking_type_id').mapped(
                             'warehouse_id').id or False,
                         'material_type': 'sheets' if self.length_in > 0 else 'coil',
                         'stock_status': 'transit',
                         'width_in': self.width_in,
                         'thickness_in': self.thickness_in,
                         'length_in': self.length_in,
                         'heat_number': self.offer_id.heat_number if self.offer_id.heat_number else '',
                         'tag_number': self.offer_id.batch if self.offer_id.batch else '',
                         'comp_c': self.offer_id.comp_c,
                         'comp_mn': self.offer_id.comp_mn,
                         'comp_p': self.offer_id.comp_p,
                         'comp_s': self.offer_id.comp_s,
                         'comp_si': self.offer_id.comp_si,
                         'comp_al': self.offer_id.comp_al,

                         'comp_ti': self.offer_id.comp_ti,
                         'comp_nb': self.offer_id.comp_nb,
                         'comp_b': self.offer_id.comp_b,
                         'comp_cu': self.offer_id.comp_cu,
                         'comp_co': self.offer_id.comp_co,
                         'comp_cr': self.offer_id.comp_cr,
                         'comp_mo': self.offer_id.comp_mo,
                         'comp_n': self.offer_id.comp_n,
                         'comp_ni': self.offer_id.comp_ni,
                         'comp_v': self.offer_id.comp_v,
                         # 'comp_pb': self.offer_id.comp_pb,
                         # 'comp_as': self.offer_id.comp_as,

                         })
                    lot_a._onchange_thickness()
                    lot_a._onchange_width()
                    lot_a._onchange_length()
                    line.lot_id = lot_a.id
                    line.lot_name = lot_a.name
                else:
                    raise UserError(_('Please provide the quantity.'))

    def get_serial_barcode(self):
        return self.env.ref('odx_product_custom_steel.action_report_serial_barcode_for_lot_picking').report_action(self)
        # return self.env.ref('odx_product_custom_steel.action_report_serial_barcode_for_lot').report_action(self)

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'current',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_owner=self.picking_type_id.code != 'incoming',
                show_lots_m2o=self.has_tracking != 'none' and (
                        picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.picking_type_id.code != 'incoming',
                show_destination_location=self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
            ),
        }
