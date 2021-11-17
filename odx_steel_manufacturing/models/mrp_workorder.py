# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def generate_lot(self):
        if not self.finished_lot_id:
            sequence = self.env['ir.sequence'].next_by_code('stock.lot.serial.custom')
            wt_kg = (self.qty_producing * 0.453592)
            lot_a = self.env['stock.production.lot']. \
                create(
                {'name': str(sequence),
                 'product_id': self.product_id.id,
                 'company_id': self.env.company.id,
                 'product_qty': self.qty_producing,
                 'weight_kg': wt_kg,
                 'weight_lb': self.qty_producing,
                 'sub_category_id': self.product_id.categ_id.id,
                 'category_id': self.product_id.categ_id.parent_id.id,
                 'product_template_id': self.product_id.product_tmpl_id.id,
                 # 'po_number': self.origin,
                 # 'vendor_serial_number': self.mapped('picking_id').mapped('partner_id').vendor_serial_number or '',
                 # 'vendor_id': self.mapped('picking_id').mapped('partner_id').id or False,
                 # 'loc_city': self.mapped('picking_id').mapped('picking_type_id').mapped(
                 #     'default_location_dest_id').id or False,
                 # 'loc_warehouse': self.mapped('picking_id').mapped('picking_type_id').mapped(
                 #     'warehouse_id').id or False,

                 })
            self.finished_lot_id = lot_a.id
            # self.lot_name = lot_a.name
        else:
            raise UserError(_('Lot is already generated for this quantity.'))

        return {
            'name': _('Stock Production Lot'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.production.lot',
            'res_id': self.finished_lot_id.id,
            'views': [(False, 'form')],
            'view_id': 'stock.view_production_lot_form',
            'target': 'new',
            # 'context': {

            # }
        }