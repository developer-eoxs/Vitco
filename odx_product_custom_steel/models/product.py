from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_product_components(self):
        component_list = ['C', 'MN', 'P', 'S', 'SI', 'AL', 'CR', 'NB', 'TI', 'CA', 'N', 'NI', 'CU', 'V', 'B']
        ids = []
        for item in component_list:
            data = {
                'name': item,
                'value': 0.0
            }
            ids.append((0, 0, data))
        return ids

    coil_number = fields.Char(string='Coilnumber')

    quality = fields.Char(string='Quality')
    location = fields.Char(string='Location')

    width_in = fields.Float(string='Width(in)')
    width_mm = fields.Float(string='Width(mm)')
    thickness_in = fields.Float(string='Thickness(in)')
    thickness_mm = fields.Float(string='Thickness(mm)')
    thickness_spec = fields.Char(string='Thickness Spec')
    length_in = fields.Float(string='Length(in)')
    length_mm = fields.Float(string='Length(mm)')
    weight_lb = fields.Float(string='Weight(lb)')
    weight_kg = fields.Float(string='Weight(Kg)')
    piw = fields.Char(string='PIW')

    grade = fields.Char(string='Grade')
    vendor_id = fields.Char(string='Vendor(id)')

    rockwell = fields.Float(string='Rock_well')
    yield_mpa = fields.Float(string='Yield(mpa)')
    yield_psi = fields.Float(string='Yield(psi)')
    tensile_mpa = fields.Float(string='Tensile(mpa)')
    tensile_psi = fields.Float(string='Tensile(psi)')
    elongation = fields.Float(string='Elongation')
    material_type = fields.Selection([('sheet', 'Sheet'), ('coil', 'Coil')],
                                     string='Type', default='coil')
    component_ids = fields.One2many('product.components', 'component_id', default=_default_product_components)

    @api.onchange('width_in')
    def _onchange_width(self):
        self.width_mm = self.width_in * 25.4

    @api.onchange('thickness_in')
    def _onchange_thickness(self):
        self.thickness_mm = self.thickness_in * 25.4

    @api.onchange('length_in')
    def _onchange_length(self):
        self.length_mm = self.length_in * 25.4

    @api.onchange('weight_lb')
    def _onchange_weight(self):
        self.weight_kg = self.weight_lb * 0.45359237

    @api.onchange('yield_mpa')
    def _onchange_yield(self):
        self.yield_psi = self.yield_mpa * 145.038

    @api.onchange('tensile_mpa')
    def _onchange_tensile(self):
        self.tensile_psi = self.tensile_mpa * 145.038

    def name_get(self):
        res = []
        for record in self:
            if not record.default_code:
                return super(ProductTemplate, self).name_get()

            name = record.name
            if record.default_code:
                name = name
            res.append((record.id, name))
        return res



        # res = []
        # for category in self:
        #     name = category.name
        #     if category.parent_id:
        #         name = category.name
        #     res.append((category.id, name))
        # return res

    #
    # def name_get(self):
    #     # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
    #     self.browse(self.ids).read(['name', 'default_code'])
    #     return [(template.id, '%s%s' % (template.default_code and '[%s] ' % template.default_code or '', template.name))
    #             for template in self]

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '%s' % (name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                # Filter out sellers based on the company. This is done afterwards for a better
                # code readability. At this point, only a few sellers should remain, so it should
                # not be a performance issue.
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                            variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                    ) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result


class ProductCategory(models.Model):
    _inherit = "product.category"

    def name_get(self):
        res = []
        for category in self:
            name = category.name
            if category.parent_id:
                name = category.name
            res.append((category.id, name))
        return res
