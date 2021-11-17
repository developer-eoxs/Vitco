from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductQuotation(models.Model):
    _name = "product.quotation"

    def line_duplicate(self):
        for line in self:
            line.copy()

    @api.depends('price_unit', 'product_qty')
    def _compute_amount(self):
        for rec in self:
            if rec.product_qty and rec.price_unit:
                rec.price_subtotal = rec.price_unit * rec.product_qty
            else:
                rec.price_subtotal = 0

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

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id

    @api.onchange('cwt_price')
    def get_cwt_based_unit_price(self):
        if self.cwt_price:
            self.price_unit = self.cwt_price / 100

    product_category_id = fields.Many2one('product.category', 'Master', domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category", track_visibility="onchange",
                                      domain="[('parent_id', '=', product_category_id) or [] ] ")
    product_id = fields.Many2one('product.product', string='Sub Product')
    descriptions = fields.Text(string='Description')

    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])
    product_qty = fields.Float(string='Weight')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)
    vrm_reference_id = fields.Many2one('vrm.lead', string='Vrm')
    cwt_price = fields.Float(string='CWT Price', digits=[6, 2])

    name = fields.Char(string="Description")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
