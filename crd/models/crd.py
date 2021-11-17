# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomerRelation(models.Model):
    _name = 'customer.relation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Customer",copy=False)
    date_created = fields.Date('Date', default=fields.Date.today())
    crd_product_ids = fields.One2many('customer.relation.lines', 'crd_id', string="CRD Products")
    production_lot_ids = fields.One2many('crd.lot.lines', 'crd_lot_id', string="Similar Lots")
    purchase_offer_ids = fields.Many2many(comodel_name='purchase.offer')
    quotation_ids = fields.One2many('sale.order', 'crd_id')
    count = fields.Integer(compute='_compute_quotation_count', string='Count')

    def _compute_quotation_count(self):
        for record in self:
            if record.quotation_ids:
                record.count = len(record.quotation_ids)
            else:
                record.count = 0

    def button_quotation(self):
        for rec in self:
            return {
                'name': 'Created Quotations',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('crd_id', '=', rec.id)],
            }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'customer.relation') or 'New'
        return super(CustomerRelation, self).create(vals)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        existing_crd = self.env['customer.relation'].search([('partner_id', '=', self.partner_id.id)])
        if existing_crd:
            raise UserError(_("Please check the existing CRD for the customer"))

    def select_all_lines(self):
        for line in self.production_lot_ids:
            line.select = True

    def un_select_all_lines(self):
        for line in self.production_lot_ids:
            line.select = False

    def action_search_lots(self):
        lots_list = []
        offers_list = []
        self.production_lot_ids = False
        for line in self.crd_product_ids:
            data_count = 0
            lots = self.env['stock.production.lot'].search(
                [('thickness_in', '<=', line.thickness_upper_in),
                 ('thickness_in', '>=', line.thickness_lower_in),
                 ('width_in', '<=', line.width_upper_in),
                 ('width_in', '>=', line.width_lower_in),
                 ('category_id', '=', line.category_id.id),
                 ('product_qty', '>', 0),
                 ('sub_category_id', '=', line.sub_category_id.id),
                 ('stock_status', '=', 'available'),
                 ('product_id', '=', line.product_id.id)])
            offers = self.env['purchase.offer'].search(
                [('product_category_id', '=', line.category_id.id), ('sub_category_id', '=', line.sub_category_id.id),
                 ('product_id', '=', line.product_id.id), ('width_in', '<=', line.width_upper_in),
                 ('width_in', '>=', line.width_lower_in)])
            for offer in offers:
                offers_list.append(offer.id)
            for lot in lots:
                if lot not in lots_list:
                    data_count +=1
                    lots_list.append(lot)
            line.count=data_count
        production_lot_lines = [(5, 0, 0)]
        # self.production_lot_ids = [coil for coil in lots_list]
        # rec.id = [(6, 0, [coil.id for coil in lots_list])]
        if lots_list:
            self.production_lot_ids = False
            for rec in lots_list:
                res = {
                    'category_id': rec.category_id.id,
                    'sub_category_id': rec.sub_category_id.id,
                    'lot_id': rec.id,
                    'width_in': rec.width_in,
                    'thickness_in': rec.thickness_in,
                    'product_id': rec.product_id.id,
                    'product_qty': rec.product_qty,
                    # 'company_id': self.env.user.company_id.id,
                }
                production_lot_lines.append((0, 0, res))
            self.production_lot_ids = production_lot_lines
        self.purchase_offer_ids = offers_list

    def action_create_quotation(self):
        products = []
        order_line_obj = self.env['sale.order.line']
        for line in self.production_lot_ids:
            if line.select == True:
                products.append(line)
        if len(products) > 0:
            quotation = self.env['sale.order'].create({
                'partner_id': self.partner_id.id,
                'partner_invoice_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id,
                'pricelist_id': self.partner_id.property_product_pricelist.id,
                'company_id': self.env.user.company_id.id,
                'crd_id': self.id,
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
                    'product_qty': product.lot_id.product_qty,
                }
                order_line = order_line_obj.create(order_line_data)
        elif len(products) == 0:
            raise UserError(_("Please select any products"))

    def import_crd_line_action(self):
        return {
            'name': _('Import CRD'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'import.crd.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_crd_id': self.id,
            }
        }


class CrdProductLines(models.Model):
    _name = 'customer.relation.lines'
    _inherit = ['stock.production.lot']



    crd_id = fields.Many2one('customer.relation', "CRD")

    crd_partner_id = fields.Many2one(related='crd_id.partner_id', store=True, string='Customer', readonly=False)

    # category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    # sub_category_id = fields.Many2one('product.category', string="Sub Category",
    #                                   domain="[('parent_id', '=', category_id) or [] ] ")
    width_upper_in = fields.Float(string='Wid Max(in)', digits=[6, 4])
    width_lower_in = fields.Float(string='Wid Min(in)', digits=[6, 4])
    thickness_upper_in = fields.Float(string='Thick Max(in)', digits=[6, 4])
    thickness_lower_in = fields.Float(string='Thick Min(in)', digits=[6, 4])
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, default=lambda self: self.env.company)
    count = fields.Integer(string="Matches",readonly=True)

    # product_id = fields.Many2one('product.product', "Sub Product",
    #                              domain="[('categ_id', '=', sub_category_id) or [] ] ")

    def action_search_product_by_line(self):
        lots_list = []
        for line in self:
            data_count =0
            lots = self.env['stock.production.lot'].search(
                [('thickness_in', '<=', line.thickness_upper_in),
                 ('thickness_in', '>=', line.thickness_lower_in),
                 ('width_in', '<=', line.width_upper_in),
                 ('width_in', '>=', line.width_lower_in),
                 ('category_id', '=', line.category_id.id),
                 ('product_qty', '>', 0),
                 ('sub_category_id', '=', line.sub_category_id.id),
                 ('stock_status', '=', 'available'),
                 ('product_id', '=', line.product_id.id)])
            for lot in lots:
                if lot not in lots_list:
                    data_count +=1
                    lots_list.append(lot)
            line.count = data_count
        production_lot_lines = [(5, 0, 0)]
        for rec in lots_list:
            res = {
                'category_id': rec.category_id.id,
                'sub_category_id': rec.sub_category_id.id,
                'lot_id': rec.id,
                'width_in': rec.width_in,
                'thickness_in': rec.thickness_in,
                'product_id': rec.product_id.id,
            }
            production_lot_lines.append((0, 0, res))
        return {
            'name': 'Our Inventory',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_crd_id': self.crd_id.id,
                        'default_category_id': self.category_id.id,
                        'default_sub_category_id': self.sub_category_id.id,
                        'default_width_upper_in': self.width_upper_in,
                        'default_width_lower_in': self.width_lower_in,
                        'default_thickness_upper_in': self.thickness_upper_in,
                        'default_thickness_lower_in': self.thickness_lower_in,
                        'default_product_id': self.product_id.id,
                        'default_product_line_ids': production_lot_lines,
                        }
        }


class CrdLotLines(models.Model):
    _name = 'crd.lot.lines'
    # _inherit = ['stock.production.lot']

    crd_lot_id = fields.Many2one('customer.relation', "CRD")

    select = fields.Boolean("Select")
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    lot_id = fields.Many2one('stock.production.lot', string='Lot Number',
                             domain="[('stock_status', '=', 'available') or [] ] ")
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_id = fields.Many2one('product.product', "Sub Product")
    product_qty = fields.Float(string='Weight')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    crd_id = fields.Many2one('customer.relation', "CRD Ref")
