from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    material_type = fields.Selection([('sheet', 'Sheet'), ('coil', 'Coil')],
                                     string='Type', default='coil')
    width_in = fields.Float(string='Width(in)', track_visibility="onchange", digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    thickness_ul = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[8, 4])
    weight_lb = fields.Float(string='Weight(lb)', store=True)
    density = fields.Float(string='Density', default=0.284)
    inner_dia = fields.Float(string='Inner Diameter')
    outer_dia = fields.Float(string='Outer Diameter')
    number_of_sheets = fields.Float(string='Number of Sheets')
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain=lambda self: self._get_category_list())
    product_id = fields.Many2one('product.product', 'SubProduct', domain=lambda self: self._domain_product_id())
    spec_ids = fields.One2many('product.specification', 'crm_ref_id', string="Product Specification")

    @api.onchange('category_id')
    def _get_category_list(self):
        sub_category = self.env['product.category'].search([('parent_id', '=', self.category_id.id)])
        fields_domain = [('id', 'in', sub_category.ids)]
        return {'domain': {'sub_category_id': fields_domain}}

    @api.onchange('sub_category_id')
    def _domain_product_id(self):
        if self.material_type:
            products = self.env['product.product'].search([('categ_id', '=', self.sub_category_id.id)])
            product_fields_domain = [('id', 'in', products.ids)]
            return {'domain': {'product_id': product_fields_domain, }}

    def estimation_calculator(self):

        if self.material_type == 'sheet':

            if self.thickness_in and self.width_in and self.length_in:
                vol = self.thickness_in * self.width_in * self.length_in
                sheet_area = self.width_in * self.length_in
                weight_per_sheet = vol * 0.284
                if self.number_of_sheets > 0:
                    self.weight_lb = weight_per_sheet * self.number_of_sheets
                else:
                    self.weight_lb = weight_per_sheet
                self.action_spec_based_search()

        else:
            if self.thickness_in and self.width_in and self.weight_lb:
                self.action_coil_based_search()

    def action_spec_based_search(self):
        self.spec_ids = False
        domain = []

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.sub_category_id:
            domain.append(('sub_category_id', '=', self.sub_category_id.id))
        if self.thickness_in:
            domain.append(('thickness_in', '>=', self.thickness_in))
            if self.thickness_ul and (self.thickness_ul > self.thickness_in):
                domain.append(('thickness_in', '<', self.thickness_ul))
        if self.width_in:
            domain.append(('width_in', '>=', self.width_in))
        # if self.length_in:
        #     domain.append(('length_in', '>=', self.length_in))

        product_lot = self.env['stock.production.lot'].search(domain)
        if product_lot:
            for rec in product_lot:
                if rec.product_qty > 0:
                    coil_length = sheet_length = no_of_sheet = width_wise_waste_length = length_wise_waste_length = 0
                    width_wise_waste_area = length_wise_waste_area = balance = total_sheet_weight = balance_percent = 0
                    number_of_sections = 0
                    residue_weight = 0
                    bal = bal_percent = 0
                    sheet_length = self.length_in
                    sheet_width = self.width_in
                    total_sheet_weight = self.weight_lb
                    number_of_sections = rec.width_in / sheet_width

                    if rec.width_in > 0 and rec.thickness_in > 0:
                        coil_length = rec.product_qty / (rec.width_in * rec.thickness_in * 0.284)

                        if self.length_in > 0:
                            no_of_sheet = coil_length / self.length_in

                        if rec.width_in > sheet_width:
                            width_wise_waste_length = (rec.width_in - self.width_in)
                            width_wise_waste_area = width_wise_waste_length * coil_length

                        length_wise_waste_length = coil_length - (no_of_sheet * sheet_length)
                        length_wise_waste_area = length_wise_waste_length * sheet_width
                        residue_weight = (length_wise_waste_area + width_wise_waste_area) * rec.thickness_in * 0.284
                        balance = rec.product_qty - (total_sheet_weight + residue_weight)
                        if rec.product_qty > 0:
                            balance_percent = (balance / rec.product_qty) * 100
                        if balance > 0:
                            bal = balance
                        else:
                            bal = 0
                        if balance_percent > 0:
                            bal_percent = balance_percent
                        else:
                            bal_percent = 0

                        total_wastage = (width_wise_waste_area + length_wise_waste_area) * (rec.thickness_in * 0.284)
                        total_wastage_percent = (total_wastage / rec.weight_lb) * 100
                        # print(total_wastage_percent)
                        # print(coil_length, no_of_sheet, length_wise_waste_area, width_wise_waste_area)
                    self.write({
                        'spec_ids': [(0, 0, {
                            'lot_id': rec.id,
                            'product_id': rec.product_id.id,
                            'category_id': rec.product_id.categ_id.parent_id.id,
                            'sub_category_id': rec.product_id.categ_id.id,
                            'weight_lb': rec.product_qty,
                            'product_uom_id': rec.product_uom_id.id,
                            'thickness_in': rec.thickness_in,
                            'width_in': rec.width_in,
                            'length_in': rec.length_in,
                            'number_of_sheets': no_of_sheet,
                            'wastage': residue_weight,
                            'balance': bal,
                            'balance_percent': bal_percent
                        })]
                    })

    def action_coil_based_search(self):
        self.spec_ids = False
        domain = []

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.sub_category_id:
            domain.append(('sub_category_id', '=', self.sub_category_id.id))
        if self.thickness_in:
            domain.append(('thickness_in', '>=', self.thickness_in))
            if self.thickness_ul and (self.thickness_ul > self.thickness_in):
                domain.append(('thickness_in', '<', self.thickness_ul))
        if self.width_in:
            domain.append(('width_in', '>=', self.width_in))

        product_lot = self.env['stock.production.lot'].search(domain)
        if product_lot:
            for rec in product_lot:
                coil_length = input_width = width_wise_waste_length = length_wise_waste_length = 0
                width_wise_waste_area = length_wise_waste_area = balance = total_sheet_weight = balance_percent = 0
                number_of_sections = 0
                bal = bal_percent = 0
                residue_weight = 0
                input_width = self.width_in
                input_weight = self.weight_lb
                number_of_sections = rec.width_in / input_width

                if rec.width_in > 0 and rec.thickness_in > 0:
                    coil_length = rec.product_qty / (rec.width_in * rec.thickness_in * 0.284)

                    if rec.width_in > input_width:
                        width_wise_waste_length = (rec.width_in - input_width)
                        width_wise_waste_area = width_wise_waste_length * coil_length
                        residue_weight = (width_wise_waste_area * rec.thickness_in) * 0.284
                    # length_wise_waste_length = coil_length - (no_of_sheet * sheet_length)
                    # length_wise_waste_area = length_wise_waste_length * sheet_width
                    balance = rec.product_qty - (input_weight + residue_weight)
                    if rec.product_qty > 0:
                        balance_percent = (balance / rec.product_qty) * 100
                    if balance > 0:
                        bal = balance
                    else:
                        bal = 0
                    if balance_percent > 0:
                        bal_percent = balance_percent
                    else:
                        bal_percent = 0

                    # total_wastage = (width_wise_waste_area + length_wise_waste_area) * (rec.thickness_in * 0.284)
                    # total_wastage_percent = (total_wastage / rec.weight_lb) * 100

                self.write({
                    'spec_ids': [(0, 0, {
                        'lot_id': rec.id,
                        'product_id': rec.product_id.id,
                        'category_id': rec.product_id.categ_id.parent_id.id,
                        'sub_category_id': rec.product_id.categ_id.id,
                        'weight_lb': rec.product_qty,
                        'product_uom_id': rec.product_uom_id.id,
                        'thickness_in': rec.thickness_in,
                        'width_in': rec.width_in,
                        'length_in': rec.length_in,
                        # 'number_of_sheets': no_of_sheet,
                        'wastage': residue_weight,
                        'balance': bal,
                        'balance_percent': bal_percent
                    })]
                })

        # if product_lot:
        #     for rec in product_lot:
        #         coil_length = sheet_length = no_of_sheet = width_wise_waste_length = length_wise_waste_length = 0
        #         width_wise_waste_area = length_wise_waste_area = 0
        #         number_of_sections =0
        #         sheet_length = self.length_in
        #         sheet_width = self.width_in
        #         number_of_sections = rec.width_in/sheet_width
        #
        #         if rec.width_in > 0 and rec.thickness_in > 0:
        #             coil_length = rec.product_qty / (rec.width_in * rec.thickness_in * 0.284)
        #
        #             if self.length_in > 0:
        #                 no_of_sheet = coil_length / self.length_in
        #
        #             if rec.width_in > sheet_width:
        #                 width_wise_waste_length = (rec.width_in - self.width_in)
        #                 width_wise_waste_area = width_wise_waste_length * coil_length
        #
        #             length_wise_waste_length = coil_length - (no_of_sheet * sheet_length)
        #             length_wise_waste_area = length_wise_waste_length * sheet_width
        #
        #             total_wastage = (width_wise_waste_area + length_wise_waste_area) * (rec.thickness_in * 0.284)
        #             total_wastage_percent = (total_wastage/rec.weight_lb)*100
        #             print(total_wastage_percent)
        #             # print(coil_length, no_of_sheet, length_wise_waste_area, width_wise_waste_area)
        #         self.write({
        #             'spec_ids': [(0, 0, {
        #                 'lot_id': rec.id,
        #                 'product_id': rec.product_id.id,
        #                 'category_id': rec.product_id.categ_id.parent_id.id,
        #                 'sub_category_id': rec.product_id.categ_id.id,
        #                 'weight_lb': rec.product_qty,
        #                 'product_uom_id': rec.product_uom_id.id,
        #                 'thickness_in': rec.thickness_in,
        #                 'width_in': rec.width_in,
        #                 'length_in': rec.length_in,
        #                 'number_of_sheets': no_of_sheet,
        #                 'wastage': total_wastage,
        #                 'wastage_percent': total_wastage_percent,
        #             })]
        #         })
