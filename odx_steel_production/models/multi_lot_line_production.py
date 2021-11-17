from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionMultiLotLine(models.Model):
    _name = 'pro.multi.lot.line'
    _description = 'Production Multi Lot'

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.category_id = self.lot_id.category_id.id if self.lot_id.category_id else False
        self.sub_category_id = self.lot_id.sub_category_id.id if self.lot_id.sub_category_id else False
        self.product_id = self.lot_id.product_id.id if self.lot_id.product_id else False
        self.product_qty = self.lot_id.product_qty
        self.width_in = self.lot_id.width_in
        self.thickness_in = self.lot_id.thickness_in
        self.product_uom_id = self.lot_id.product_uom_id.id if self.lot_id.product_uom_id else False
        self.lot_status = self.lot_id.stock_status
        self.src_warehouse_id = self.lot_id.loc_warehouse.id
        # self.dest_warehouse_id = self.lot_id.loc_warehouse.id

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Lot", track_visibility='onchange',
                             domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available'), ])
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Sub Product')
    product_qty = fields.Float(string='Weight')
    width_in = fields.Float(string='Width(in)',digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    pro_ref_id = fields.Many2one('steel.production', string='Production Ref')
    src_warehouse_id = fields.Many2one('stock.warehouse', 'Source WH',
                                       required=True)
    number_of_parts = fields.Integer(string='No.Of Parts')
    number_of_bundles = fields.Integer(string='No.Of Bundles', default=1)
    number_of_slits = fields.Integer(string='No.Of Slits', default=1)
    lot_pricing = fields.Float(string='Pricing', digits=[6, 4])

    lot_status = fields.Selection([
        ('transit', 'In Transit'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('not_available', 'Not available')
    ], string='Stock Status', track_visibility="onchange")

    def add_product_to_line(self):
        # bal_wt = bal_width = 0
        # for rec in self.job_order_ref_id.job_line_ids:
        #     if rec.lot_id == self.lot_id:
        #         bal_wt = self.product_qty - rec.product_qty
        #         bal_width = self.width_in - rec.width_in
        if self.lot_id:
            if self.pro_ref_id.operation == 'parting':
                if self.number_of_parts > 0:
                    i = 0
                    while i < self.number_of_parts:
                        self.pro_ref_id.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
                                'category_id': self.category_id.id,
                                'sub_category_id': self.sub_category_id.id,
                                'product_qty': self.product_qty / self.number_of_parts,
                                'product_uom_id': self.product_uom_id.id,
                                'thickness_in': self.thickness_in,
                                'material_type': 'coil',
                                'width_in': self.width_in / self.number_of_parts,

                            })]
                        })
                        i += 1

            elif self.pro_ref_id.operation == 'cutting':
                if self.number_of_bundles > 0:
                    i = 0
                    while i < self.number_of_bundles:
                        self.pro_ref_id.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
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


            elif self.pro_ref_id.operation == 'slitting':
                if self.number_of_slits > 0:
                    i = 0
                    while i < self.number_of_slits:
                        self.pro_ref_id.write({
                            'production_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
                                'category_id': self.category_id.id,
                                'sub_category_id': self.sub_category_id.id,
                                'product_qty': int(self.product_qty / self.number_of_slits),
                                'product_uom_id': self.product_uom_id.id,
                                'thickness_in': self.thickness_in,
                                'material_type': 'coil',
                                'width_in': self.width_in/self.number_of_slits,

                            })]
                        })
                        i += 1
            elif self.pro_ref_id.operation == 'multistage':
                self.pro_ref_id.write({
                    'multi_stage_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        'product_uom_id': self.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'material_type': 'coil',
                        # 'width_in': self.width_in,

                    })]
                })
            elif self.pro_ref_id.operation == 'annealing':
                self.pro_ref_id.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        'product_uom_id': self.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'material_type': 'coil',
                        'width_in': self.width_in,
                        'product_qty': self.product_qty,

                    })]
                })
            elif self.pro_ref_id.operation == 'cr':
                self.pro_ref_id.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
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
                self.pro_ref_id.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.lot_id.id,
                        'product_id': self.pro_ref_id.order_line_product.id if self.pro_ref_id.order_line_product else self.product_id.id,
                        'category_id': self.category_id.id,
                        'sub_category_id': self.sub_category_id.id,
                        # 'product_qty': self.product_qty,
                        'product_uom_id': self.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'material_type': 'coil',
                        'width_in': self.width_in,

                    })]
                })

