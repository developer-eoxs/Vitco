from odoo import models, fields, api, _

# from odoo.exceptions import UserError
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_freight_done = fields.Boolean(string="Is freight done", default=False, copy=False)
    freight_id = fields.Many2one('freight.management', string="Freight Id", copy=False)

    def generate_freight(self):
        if self.env.user.has_group('odx_freight_management.group_frm_view_access'):
            freight_object = self.env['freight.management']
            vals = {
                'purchase_order_id': self.purchase_id.id,
                'stock_picking_id': self.id,
                'cargo_lines': []
            }
            for operation in self.move_ids_without_package:
                if not operation.move_line_nosuggest_ids.mapped('lot_id').ids:
                    raise UserError(_('Please Generate Lots !!'))
                vals['cargo_lines'].append((0, 0, {
                    'name': operation.description,
                    'sub_category_id': operation.sub_category_id and operation.sub_category_id.id,
                    'product_uom_qty': operation.product_uom_qty,
                    'product_id': operation.product_id and operation.product_id.id,
                    'lot_ids': [(6, 0, operation.move_line_nosuggest_ids.mapped('lot_id').ids)],
                }))
            new_freight = freight_object.create(vals)
            self.freight_id = new_freight.id
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
        else:
            raise UserError(_("You do not have the permission to access Freights. Please contact admin"))

    # def generate_freight(self):
    #     freight_object = self.env['freight.management']
    #     new_freight = freight_object.create({
    #         'purchase_order_id': self.purchase_id.id,
    #         'stock_picking_id': self.id,
    #     })
    #
    #     return {
    #         'name': 'Freight Management',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'freight.management',
    #         'view_id': False,
    #         'target': 'current',
    #         'res_id': new_freight.id,
    #         'type': 'ir.actions.act_window',
    #     }

    def action_view_freights(self):
        if self.env.user.has_group('odx_freight_management.group_frm_view_access'):
            picking_id_list = []
            freight_picking = self.env['freight.management'].search([('stock_picking_id', '=', self.id)])
            if freight_picking:
                picking_id_list.append(freight_picking.id)
            if picking_id_list:
                return {
                    'name': 'Freight Management',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'freight.management',
                    'view_id': False,
                    'target': 'current',
                    'domain': [('id', '=', picking_id_list)],
                    'type': 'ir.actions.act_window',
                }
            else:
                raise UserError(_('No freights are assigned.'))
        else:
            raise UserError(_("You do not have the permission to access Freights. Please contact admin"))

    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     if not self.env.context.get('baby_lot'):
    #         if self.picking_type_id.code == "incoming":
    #             if not self.is_freight_done:
    #                 raise UserError(_('Freight Movement is under progress. Please validate after the freight movement '
    #                                   'is complete'))
    #     return res
