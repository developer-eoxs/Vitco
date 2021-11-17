from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError

from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.send_back_status = 'done'
        for line in self.order_line:
            if line.lot_id:
                line.lot_id.stock_status = 'reserved'
                # line.lot_id.stock_status = 'reserved'
        return res

    def action_view_productions(self):
        lines = []
        if self.env.user.has_group('odx_steel_production.group_production_view_access'):
            if self.order_line:
                lines = self.mapped('order_line')
            return {
                'name': _('Production'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'steel.production',
                'view_id': False,
                'domain': [('sale_line_id', 'in', lines.ids)],
                'context': {
                    'search_default_sale_line_id': 'sale_line_id'
                    # 'search_default_sale_line_id': 1,
                    # 'default_group_by_sale_line_id': 1
                }
            }
        else:
            raise UserError(_("You do not have the permission to access Production. Please contact admin"))

    def action_view_job_orders(self):
        lines = []
        if self.env.user.has_group('odx_steel_production.group_production_view_access'):
            if self.order_line:
                lines = self.mapped('order_line')
            return {
                'name': _('Job Orders'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'job.order',
                'view_id': False,
                'domain': [('sale_line_id', 'in', lines.ids)],
                'context': {
                    'search_default_sale_line_id': 'sale_line_id'
                    # 'search_default_sale_line_id': 1,
                    # 'default_group_by_sale_line_id': 1
                }
            }
        else:
            raise UserError(_("You do not have the permission to access Job Orders. Please contact admin"))

    def _compute_production_count(self):
        lines = []
        if self.order_line:
            lines = self.mapped('order_line').mapped('production_lot_ids')
        self.production_count = len(lines)

    def _compute_job_order_count(self):
        lines = []
        if self.order_line:
            lines = self.mapped('order_line').mapped('job_lot_ids')
        self.job_order_count = len(lines)

    @api.onchange('category_id', )
    def _get_category_list(self):
        self.product_id = False
        if self.category_id:
            fields_domain = [('parent_id', '=', self.category_id.id)]
            return {'domain': {'sub_category_id': fields_domain, }}
        else:
            return {'domain': {'sub_category_id': []}}

    @api.onchange('warehouse_id')
    def onchange_order_warehouse(self):
        for line in self.order_line:
            if line.lot_id:
                line.product_id = False
                line.lot_id = False
            else:
                line.product_id = False

    @api.onchange('category_id', 'sub_category_id')
    def _domain_product_id(self):
        # self.product_id = False
        if self.sub_category_id:
            return {'domain': {'product_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_id': []}}

    def update_status(self):
        lot_list = []
        option_line_list = []
        similar_options = []
        table = ''
        table += '''<p>The following coils are associated with some orders:                
                    </p>
                    <br/>
                    <table class="table table-bordered">
                <thead>
                    <tr>
                        <td><b><font style="color: #2196F3;">Lot Number</font></b><br></td>
                        <td><b><font style="color: #2196F3;">Order/Quotation</font></b><br></td>
                        <td><b><font style="color: #2196F3;">Order State</font></b><br></td>           
                    </tr>
                </thead>
                <tbody>
                 '''
        order_lines_list = self.env['sale.order.line'].search([])
        for rec in self.order_line:
            lot_list.append(rec.lot_id.id)

        for rec in self.sale_order_option_ids:
            if rec.select:
                option_line_list.append(rec.lot_id.id)

        for lines in order_lines_list:
            if ((lines.lot_id.id in lot_list) or (lines.lot_id.id in option_line_list)):
                if not lines.order_id.id == self.id:
                    similar_options.append((0, 0, {'name': lines.order_id.name,
                                                   'state': lines.order_id.state}))
                    table += '''
                                                            <tr>
                                                                <td><b><font style="color: #000000;">''' + str(
                        lines.lot_id.name) + '''</font></b><br></td>
                                                                <td><b><font style="color: #000000;">''' + str(
                        lines.order_id.name) + '''</font></b><br></td>
                                                                <td><b><font style="color: #000000;">''' + str(
                        lines.order_id.state) + '''</font></b><br></td>              
                                                            </tr>
                                                            '''
        table += ''' </tbody>
                      </table>
                       '''

        if similar_options:
            return {
                'name': _('Similar Options'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'display.options.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_memo': table,
                    'default_sale_order_id': self.id}
            }

        else:
            table = '''<p>No coils are used in Other orders, You are good to go.               
                                       </p>'''
            return {
                'name': _('Similar Options'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'display.options.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_memo': table,
                    'default_sale_order_id': self.id}
            }
            # self.verify_options()

    def verify_options(self):
        if self.send_back_status == 'option_received' or self.send_back_status == 'option_send':
            self.write({
                # 'state': 'sent',
                'is_quotation_sent': False
            })

    def verify_option_on_direct_sale(self):
        # if self.order_line:
        return self.update_status()

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('send_options'):
            self.sudo().verify_options()
        else:
            self.is_quotation_sent = True
            self.send_back_status = 'quote_send'
            self.is_send_back = True
            self.require_signature = True
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def compute_option_status(self):
        for rec in self:
            rec.option_status = rec.state

    def update_price_on_line(self):
        product_list = []
        sub_category_list = []
        lines = []

        for line in self.order_line:
            if line.sub_category_id.id not in sub_category_list:
                sub_category_list.append(line.sub_category_id.id)
        if sub_category_list:
            for rec in sub_category_list:
                for line in self.order_line:
                    if line.sub_category_id.id == rec:
                        if line.product_id.id not in product_list:
                            product_list.append(line.product_id.id)
                            lines.append((0, 0, {

                                'product_id': line.product_id.id,
                                'category_id': line.category_id.id,
                                'sub_category_id': rec,
                                'line_price': line.price_unit

                            }))
        return {
            'name': _('Update Price'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'update.price.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_price_line_ids': lines,
                'default_sale_order_id': self.id,
            }
        }

    option_status = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Options Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Option Status', compute='compute_option_status')

    is_send_back = fields.Boolean(string="Send back", default=False, copy=False)
    production_count = fields.Integer(string="Count", compute="_compute_production_count")
    job_order_count = fields.Integer(string="JobCount", compute="_compute_job_order_count")
    is_quotation_sent = fields.Boolean(string="Quotation Status Check", default=False, copy=False)
    send_back_status = fields.Selection([
        ('option_send', 'Send Options'),
        ('option_received', 'Options Received'),
        ('quote_send', 'Quote Send'),
        ('done', 'Done'),
    ], string='Request Quote Status', required=True, copy=False, default='option_send')
    # spec_ids = fields.One2many('product.specification', 'sale_ref_id', string="Product Specification")
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    # domain="['|',('parent_id', '=', category_id),('active','=',True)]")
    # domain="['|',('parent_id', '=', category_id),(1,'=',1)] ")
    # domain=lambda self: self._get_category_list())

    product_id = fields.Many2one('product.product', 'Sub Product',
                                 domain="[('categ_id', '=', sub_category_id) or [] ] ")

    coil_search = fields.Char(string='Search By Coil Number')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    width_ibt = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    thickness_ibt = fields.Float(string='Thickness(in)', digits=[6, 4])
    width_operator = fields.Selection([
        ('=', 'Equal'),
        ('>', 'Greater than'), ('>=', 'Greater than or equal to'), ('ibt', 'In Between'),
        ('<', 'Less Than'), ('<=', 'Less than or equal to')], string='Width Operator')
    thickness_operator = fields.Selection([
        ('=', 'Equal'),
        ('>', 'Greater than'), ('>=', 'Greater than or equal to'), ('ibt', 'In Between'),
        ('<', 'Less Than'), ('<=', 'Less than or equal to')], string='Thickness Operator')

    def action_search_product(self):
        domain = [('stock_status', '=', 'available'), ('loc_warehouse', '=', self.warehouse_id.id)]
        if self.sale_order_option_ids:
            opt_lines = []
            opt_lines = self.sale_order_option_ids.mapped('lot_id').ids
            domain.append(('id', 'not in', opt_lines))
        if not self.coil_search:
            if self.product_id:
                domain.append(('product_id', '=', self.product_id.id))
            if self.sub_category_id:
                domain.append(('sub_category_id', '=', self.sub_category_id.id))

            if self.thickness_operator:
                if not self.thickness_operator == 'ibt':
                    domain.append(('thickness_in', self.thickness_operator, self.thickness_in))
                else:
                    domain.append(('thickness_in', '<', self.thickness_ibt))
                    domain.append(('thickness_in', '>', self.thickness_in))
            if self.width_operator:
                if not self.width_operator == 'ibt':
                    domain.append(('width_in', self.width_operator, self.width_in))
                else:
                    domain.append(('width_in', '<', self.width_ibt))
                    domain.append(('width_in', '>', self.width_in))
        else:
            self.action_clear_option_lines()
            domain.append(('name', '=', self.coil_search))

        product_lot = self.env['stock.production.lot'].search(domain)

        if product_lot:
            for rec in product_lot:
                if rec.product_qty > 0:
                    self.write({
                        'sale_order_option_ids': [(0, 0, {
                            'lot_id': rec.id,
                            'product_id': rec.product_id.id,
                            'name': rec.product_id.name,
                            'category_id': rec.product_id.categ_id.parent_id.id,
                            'sub_category_id': rec.product_id.categ_id.id,
                            'quantity': rec.product_qty,
                            'uom_id': rec.product_uom_id.id,
                            'thickness_in': rec.thickness_in,
                            'width_in': rec.width_in,
                            'price_unit': rec.product_id.lst_price,

                        })]
                    })

    def select_all_lines(self):
        for line in self.sale_order_option_ids:
            line.select = True

    def un_select_all_lines(self):
        for line in self.sale_order_option_ids:
            line.select = False

    def action_clear_option_lines(self):
        option_lines = self.sale_order_option_ids.filtered(lambda l: l.select == False and l.is_present == False)

        for rec in option_lines:
            rec.unlink()

    def action_update_order_line(self):
        domain = []
        line_object = self.env['sale.order.line']

        # self.order_line = False
        option_lines = self.sale_order_option_ids.filtered(lambda l: l.select == True and l.is_present == False)
        for line in option_lines:
            if line.select:
                new_order_line = line_object.sudo().create({
                    'order_id': self.id,
                    'lot_id': line.lot_id.id,
                    'product_id': line.product_id.id,
                    'category_id': line.category_id.id,
                    'sub_category_id': line.sub_category_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.uom_id.id,
                    'thickness_in': line.thickness_in,
                    'width_in': line.width_in,
                    'price_unit': line.product_id.lst_price,
                    'material_type': line.lot_id.material_type
                })
                new_order_line.product_id_change()

    def send_optional_products(self):
        self.ensure_one()

        template_id = self.env.ref('odx_product_custom_steel.mail_template_sale_eoxs').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'send_options': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'name': _('Send Options'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     procurements = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
    #             continue
    #         qty = line._get_qty_procurement(previous_product_uom_qty)
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
    #             continue
    #
    #         group_id = line._get_procurement_group()
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             updated_vals = {}
    #             if group_id.partner_id != line.order_id.partner_shipping_id:
    #                 updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #             if group_id.move_type != line.order_id.picking_policy:
    #                 updated_vals.update({'move_type': line.order_id.picking_policy})
    #             if updated_vals:
    #                 group_id.write(updated_vals)
    #
    #         values = line._prepare_procurement_values(group_id=group_id)
    #         product_qty = line.product_uom_qty - qty
    #
    #         line_uom = line.product_uom
    #         quant_uom = line.product_id.uom_id
    #         product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
    #         procurements.append(self.env['procurement.group'].Procurement(
    #             line.product_id, product_qty, procurement_uom,
    #             line.order_id.partner_shipping_id.property_stock_customer,
    #             line.name, line.order_id.name, line.order_id.company_id, values, line.id))
    #     if procurements:
    #         self.env['procurement.group'].run(procurements)
    #     return True

    # def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #     other_lines = self.filtered(lambda line: line.lot_id == False)
    #     print(other_lines, "other_lines")
    #     return super(SaleOrderLine, other_lines)._action_launch_stock_rule(previous_product_uom_qty)

    # def action_show_lot_details(self):
    #     if self.lot_id:
    #         return {
    #             'name': _('Lot Details'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'stock.production.lot',
    #             'view_id': False,
    #             'res_id': self.lot_id.id,
    #             'domain': [('id', '=', self.lot_id.id)],
    #         }
    def line_duplicate(self):
        for line in self:
            line.copy(default={'order_id': self.order_id.id,
                               'lot_id': False})

    @api.onchange('category_id', )
    def _get_category_list(self):

        if self.category_id:
            fields_domain = [('parent_id', '=', self.category_id.id)]
            return {'domain': {'sub_category_id': fields_domain, }}
        else:
            return {'domain': {'sub_category_id': []}}

    @api.onchange('category_id', 'sub_category_id')
    def _domain_product_id(self):

        if self.sub_category_id:
            return {'domain': {'product_id': [('categ_id', '=', self.sub_category_id.id)]}}
        else:
            return {'domain': {'product_id': []}}

    @api.onchange('sub_category_id', 'product_id')
    def _domain_lot_id(self):
        if self.product_id:
            return {'domain': {'lot_id': [('product_id', '=', self.product_id.id), ('stock_status', '=', 'available'),
                                          ('loc_warehouse', '=', self.order_id.warehouse_id.id)]}}
        else:
            if self.sub_category_id and not self.product_id:
                return {'domain': {
                    'lot_id': [('sub_category_id', '=', self.sub_category_id.id), ('stock_status', '=', 'available'),
                               ('loc_warehouse', '=', self.order_id.warehouse_id.id)]}}

    @api.onchange('lot_id')
    def lot_based_products(self):
        if not self.sub_category_id:
            self.sub_category_id = self.lot_id.sub_category_id.id
        if not self.category_id:
            self.category_id = self.lot_id.category_id.id
        if not self.product_id:
            self.product_id = self.lot_id.product_id.id
        self.product_uom_qty = self.lot_id.product_qty
        self.product_uom = self.lot_id.product_uom_id.id
        self.thickness_in = self.lot_id.thickness_in
        self.width_in = self.lot_id.width_in
        self.material_type = self.lot_id.material_type

    @api.onchange('parent_warehouse_id')
    def parent_warehouse_onchange(self):
        if self.parent_warehouse_id:
            return {'domain': {'lot_id': [('stock_status', '=', 'available'),
                                          ('loc_warehouse', '=', self.parent_warehouse_id.id)]}}

    @api.onchange('cwt_price')
    def get_cwt_based_unit_price(self):
        if self.cwt_price:
            self.price_unit = self.cwt_price / 100

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    lot_id = fields.Many2one('stock.production.lot', string='Lot Number',
                             domain="[('stock_status', '=', 'available')] or []")
    #
    # domain=lambda self: self._domain_lot_id())
    produced_lot_ids = fields.Many2many('stock.production.lot', string='Lot Produced', copy=False)

    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])
    # number_of_sheets = fields.Float(string='No.of Sheets')
    production_lot_ids = fields.One2many('steel.production', 'sale_line_id', string='Production')
    job_lot_ids = fields.One2many('job.order', 'sale_line_id', string='Job Orders')
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type', track_visibility="onchange")

    parent_warehouse_id = fields.Many2one('stock.warehouse', store=True, string='Warehouse', readonly=False)
    cwt_price = fields.Float(string='CWT Price', digits=[6, 2])

    width_tolerance_min = fields.Float(string='Width Tolerance(min)', digits=[6, 4])
    width_tolerance_max = fields.Float(string='Width Tolerance(max)', digits=[6, 4])
    gauge_tolerance_min = fields.Float(string='Gauge Tolerance(min)')
    gauge_tolerance_max = fields.Float(string='Gauge Tolerance(max)')
    dia_id = fields.Float(string='ID')
    dia_od_min = fields.Float(string='OD(min)')
    dia_od_max = fields.Float(string='OD(min)')
    rockwell_min = fields.Float(string='Rockwell(min)', digits=[6, 1])
    rockwell_max = fields.Float(string='Rockwell(max)', digits=[6, 1])
    part_no = fields.Text(string='Part Number')
    fork_lift = fields.Text(string='Forklift')
    certsreq = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='CertsReq ', default='yes')
    spacers = fields.Integer(string='Spacers ')
    mx_skid_wt = fields.Char(string='Max Skid Wt.')
    over_head_crar = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Over Head Crar', default='yes')

    def action_view_order(self):
        action = {
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('odx_product_custom_steel.button_sale_order_line_form').id, 'form')],
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'name': _('Sale Order lines'),
            'res_model': 'sale.order.line', }
        return action

    def action_production_wizard(self):
        wizard = self.env['production.wizard'].create({
            'category_id': self.category_id.id,
            'sub_category_id': self.sub_category_id.id,
            'product_id': self.product_id.id,
            'width_in': self.width_in,
            'thickness_in': self.thickness_in,
            'weight_lb': self.product_uom_qty,
            'width_operator': '>=',
            'thickness_operator': '=',
            'sale_line_id': self.id,
            'description': self.name,
            'length_in': self.length_in,
            'material_type': self.material_type,
            'sale_order_id': self.order_id.id,
            'warehouse_id': self.order_id.warehouse_id.id
        })
        wizard.action_search_product()
        return {
            'name': _('Production Process'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'production.wizard',
            'res_id': wizard.id,
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
        }


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    @api.onchange('category_id')
    def _get_category_list(self):
        if self.category_id:
            sub_category = self.env['product.category'].search([('parent_id', '=', self.category_id.id)])
            fields_domain = [('id', 'in', sub_category.ids)]
            return {'domain': {'sub_category_id': fields_domain, }}

    @api.onchange('sub_category_id')
    def _domain_product_id(self):
        if self.sub_category_id:
            products = self.env['product.product'].search([('categ_id', '=', self.sub_category_id.id)])
            product_fields_domain = [('id', 'in', products.ids)]
            return {'domain': {'product_id': product_fields_domain, }}

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * line.quantity
            line.update({
                'price_subtotal': price
            })

    @api.depends('line_id', 'order_id.order_line', 'product_id', 'lot_id', 'select')
    def _compute_is_present(self):
        # NOTE: this field cannot be stored as the line_id is usually removed
        # through cascade deletion, which means the compute would be false
        for option in self:
            option.is_present = bool(
                option.order_id.order_line.filtered(lambda l: l.lot_id == option.lot_id))

    def _get_values_to_add_to_order(self):
        self.ensure_one()
        return {
            'order_id': self.order_id.id,
            'price_unit': self.price_unit,
            'name': self.name,
            'lot_id': self.lot_id.id if self.lot_id else False,
            'category_id': self.category_id.id if self.category_id else False,
            'sub_category_id': self.sub_category_id.id if self.sub_category_id else False,
            'product_id': self.product_id.id if self.product_id else False,
            'width_in': self.width_in,
            'thickness_in': self.thickness_in,
            'product_uom_qty': self.quantity,
            'product_uom': self.uom_id.id if self.uom_id else False,
            'material_type': self.lot_id.material_type if self.lot_id.material_type else False,
            'discount': self.discount,
            'company_id': self.order_id.company_id.id,
        }

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]",
                                  readonly=True)
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain=lambda self: self._get_category_list(), readonly=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot Number', readonly=True)
    width_in = fields.Float(string='Width(in)', digits=[6, 4], readonly=True)
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4], readonly=True)
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    select = fields.Boolean(string='Select')
