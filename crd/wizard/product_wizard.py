# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductWizard(models.TransientModel):
    _name = 'product.wizard'
    crd_id = fields.Many2one('customer.relation', "CRD")

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    width_upper_in = fields.Float(string='Width Max(in)', digits=[6, 4])
    width_lower_in = fields.Float(string='Width Min(in)', digits=[6, 4])
    thickness_upper_in = fields.Float(string='Thickness Max(in)', digits=[6, 4])
    thickness_lower_in = fields.Float(string='Thickness Min(in)', digits=[6, 4])
    product_id = fields.Many2one('product.product', "Sub Product",
                                 domain="[('categ_id', '=', sub_category_id) or [] ] ")
    product_line_ids = fields.Many2many('product.wizard.lines', string="CRD Products")

    select_all = fields.Boolean("Select All/Un Select All")

    @api.onchange('select_all')
    def _onchange_select_all(self):
        if self.select_all == True:
            for line in self.product_line_ids:
                line.select = True
        elif self.select_all == False:
            for line in self.product_line_ids:
                line.select = False

    def action_create_quotation(self):
        products = []
        order_line_obj = self.env['sale.order.line']
        for line in self.product_line_ids:
            if line.select == True:
                products.append(line)
        if len(products) > 0:
            quotation = self.env['sale.order'].create({
                'partner_id': self.crd_id.partner_id.id,
                'partner_invoice_id': self.crd_id.partner_id.id,
                'partner_shipping_id': self.crd_id.partner_id.id,
                'pricelist_id': self.crd_id.partner_id.property_product_pricelist.id,
                'company_id': self.env.user.company_id.id,
                'crd_id': self.crd_id.id,
            })
            for product in products:
                order_line_data = {
                    'order_id': quotation.id,
                    'product_id': product.product_id.id,
                    'name': product.product_id.name,
                    'product_uom_qty': product.lot_id.product_qty,
                    'product_uom': product.product_id.uom_id.id,
                    'category_id': product.category_id.id,
                    'sub_category_id': product.sub_category_id.id,
                    'lot_id': product.lot_id.id,
                    'material_type': product.lot_id.material_type,
                    'thickness_in': product.lot_id.thickness_in,
                    'width_in': product.lot_id.width_in,
                }
                order_line = order_line_obj.create(order_line_data)
        elif len(products) == 0:
            raise UserError(_("Please select any products"))


class ProductWizardLines(models.Model):
    _name = 'product.wizard.lines'
    select = fields.Boolean("Select")
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    lot_id = fields.Many2one('stock.production.lot', string='Lot Number',
                             domain="[('stock_status', '=', 'available') or [] ] ")
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_id = fields.Many2one('product.product', "Sub Product")
