from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round, get_lang


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    thickness_ul = fields.Float('Thickness_ul(in)', digits=[6, 4])
    thickness_ll = fields.Float('Thickness_ll(in)', digits=[6, 4])
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', categ_id) or [] ] ")

    @api.onchange('categ_id')
    def _get_category_list(self):
        if self.categ_id:
            fields_domain = [('parent_id', '=', self.categ_id.id)]
            return {'domain': {'sub_category_id': fields_domain, }}
        else:
            return {'domain': {'sub_category_id': []}}

    @api.onchange('categ_id', 'sub_category_id')
    def _domain_product_id(self):
        if self.sub_category_id:
            return {'domain': {'product_tmpl_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_tmpl_id': []}}


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        self.ensure_one()
        thickness = self._context.get('thickness')
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
        if self._context.get('thickness'):

            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)
                    AND (item.thickness_ll<=%s)
                    AND (item.thickness_ul>=%s)
    
                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date, thickness, thickness))
        else:
            #
            self.env.cr.execute(
                """
                SELECT
                    item.id
                FROM
                    product_pricelist_item AS item
                LEFT JOIN product_category AS categ ON item.categ_id = categ.id
                WHERE
                    (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                    AND (item.product_id IS NULL OR item.product_id = any(%s))
                    AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                    AND (item.pricelist_id = %s)
                    AND (item.date_start IS NULL OR item.date_start<=%s)
                    AND (item.date_end IS NULL OR item.date_end>=%s)

                ORDER BY
                    item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
                """,
                (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            thickness=self.lot_id.thickness_in

        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result

    def get_sale_order_line_multiline_description_sale(self, product):
        res = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
        name = False
        if self.category_id and self.sub_category_id:
            if self.material_type:
                res = self.category_id.name + "/" + self.sub_category_id.name + "/" + self.product_id.name + " /" + self.material_type
            else:
                res = self.category_id.name + "/" + self.sub_category_id.name + "/" + self.product_id.name

        return res
