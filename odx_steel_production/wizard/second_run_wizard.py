from odoo import models, fields, api


class SecondRunWizard(models.TransientModel):
    _name = 'second.run.wizard'

    line_order_ids = fields.One2many('second.run.line.wizard', 'second_run_id', string="Order line")
    multi_stage_id = fields.Many2one('multi.stage.line')
    production_id = fields.Many2one('steel.production')
    source_lot_id = fields.Many2one('stock.production.lot', string="Source Lot")

    def action_create_second_run(self):
        if self.line_order_ids and self.production_id:
            self.production_id.production_line_ids = False
            i = 0
            line_weight = sum(self.mapped('line_order_ids').mapped('product_qty'))

            line_width = sum(self.mapped('line_order_ids').mapped('width_in'))
            line_slits = sum(self.mapped('line_order_ids').mapped('slits'))
            line_width_sum = line_width * line_slits
            line_weight_sum = line_weight * line_slits
            residual_width = self.source_lot_id.width_in - line_width_sum
            residual_weight = self.source_lot_id.product_qty - line_weight_sum

            for rec in self.line_order_ids:
                while i < rec.slits:
                    self.production_id.write({
                        'production_line_ids': [(0, 0, {
                            'lot_id': rec.lot_id.id,
                            'product_id': rec.lot_id.product_id.id,
                            'category_id': rec.lot_id.category_id.id,
                            'sub_category_id': rec.lot_id.sub_category_id.id,
                            'product_uom_id': rec.lot_id.product_uom_id.id,
                            'thickness_in': rec.thickness_in,
                            'width_in': rec.width_in,
                            'product_qty': rec.product_qty,
                            'material_type': 'coil'
                        })]
                    })
                    i += 1
            if line_weight < self.source_lot_id.product_qty:
                self.production_id.write({
                    'production_line_ids': [(0, 0, {
                        'lot_id': self.source_lot_id.id,
                        'product_id': self.source_lot_id.product_id.id,
                        'category_id': self.source_lot_id.category_id.id,
                        'sub_category_id': self.source_lot_id.sub_category_id.id,
                        'product_uom_id': self.source_lot_id.product_uom_id.id,
                        'thickness_in': self.source_lot_id.thickness_in,
                        'width_in': residual_width,
                        'product_qty': residual_weight,
                        'material_type': 'sheets',
                        'is_scrap': True
                    })]
                })
            self.source_lot_id.stock_status = 'in_production'


class SecondRunLineWizard(models.TransientModel):
    _name = 'second.run.line.wizard'

    lot_id = fields.Many2one('stock.production.lot', string="Tag")
    second_run_id = fields.Many2one('second.run.wizard', string="Second Run")
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Sub Product')
    product_qty = fields.Float(string='Weight')
    width_in = fields.Float(string='Width(in) to be cut', digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    slits = fields.Integer(string='No. of Slits')

    @api.onchange('width_in')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in:
            coil_weight = self.lot_id.product_qty
            coil_width = self.lot_id.width_in
            unit_weight = (coil_weight / coil_width)
            self.product_qty = int(unit_weight * self.width_in)
