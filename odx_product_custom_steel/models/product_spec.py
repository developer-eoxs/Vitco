from odoo import models, fields, api


class ProductSpec(models.Model):
    _name = 'product.specification'
    _order = 'wastage asc'

    lot_id = fields.Many2one('stock.production.lot', string='Lot Number')
    width_in = fields.Float(string='Width(in)',digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)',digits=[8, 4])
    length_in = fields.Float(string='Length(in)',digits=[8, 4])
    weight_lb = fields.Float(string='Weight(lb)')
    product_id = fields.Many2one('product.product', 'Sub Product')
    category_id = fields.Many2one('product.category', string="Master")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_uom_id = fields.Many2one('uom.uom', string="UOM")
    select = fields.Boolean(string="Select")
    number_of_sheets = fields.Float(string="Sheets")
    wastage = fields.Float(string="Residue")
    balance = fields.Float(string="Balance")
    balance_percent = fields.Float(string="Balance in %", digits=[4, 4])
    # sale_ref_id = fields.Many2one('sale.order', string="Crm Reference")
    crm_ref_id = fields.Many2one('crm.lead', string="Crm Reference")
    less_wastage = fields.Boolean(string="Less Wastage", compute="_compute_less_wastage")

    def _compute_less_wastage(self):
        for rec in self:
            rec.less_wastage = False
            lines = rec.mapped('crm_ref_id').mapped('spec_ids').sorted(key=lambda r: r.wastage)
            # type = rec.mapped('crm_ref_id').mapped('material_type')
            if lines:
                if self.crm_ref_id.material_type == 'sheet':

                    sheets = rec.mapped('crm_ref_id').number_of_sheets
                    spec_len = rec.mapped('crm_ref_id').mapped('spec_ids')

                    sum_of_sheets = 0
                    line_list = []
                    for i in range(0, len(spec_len)):
                        sum_of_sheets += lines[i].number_of_sheets
                        line_list.append(i)
                        if sum_of_sheets >= int(sheets):
                            for record in line_list:
                                lines[record].less_wastage = True
                            break

                if self.crm_ref_id.material_type == 'coil':
                    input_wt = rec.mapped('crm_ref_id').weight_lb
                    spec_len = rec.mapped('crm_ref_id').mapped('spec_ids')

                    sum_of_weights = 0
                    line_list = []
                    for i in range(0, len(spec_len)):
                        sum_of_weights += lines[i].weight_lb
                        line_list.append(i)
                        if sum_of_weights >= int(input_wt):
                            for record in line_list:
                                lines[record].less_wastage = True
                            break
