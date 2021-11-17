from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductionWizard(models.TransientModel):
    _name = 'production.wizard'

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

    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category",
                                      domain="[('parent_id', '=', category_id) or [] ] ")
    product_id = fields.Many2one('product.product', 'Sub Product',
                                 domain="[('categ_id', '=', sub_category_id) or [] ]")
    sale_line_id = fields.Many2one('sale.order.line', 'Order Line Ref')
    sale_order_id = fields.Many2one('sale.order', 'Order Ref')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    dest_warehouse_id = fields.Many2one('stock.warehouse', 'Dest WH')

    coil_search = fields.Char(string='Search By Coil Number')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    length_in = fields.Float(string='Length(in)', digits=[6, 4])
    # number_of_sheets = fields.Float(string='No.of Sheets')
    weight_lb = fields.Float(string='Weight(lbs)')
    description = fields.Char(string='Description')
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')

    width_ibt = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_ibt = fields.Float(string='Thickness(in)', digits=[6, 4])
    width_operator = fields.Selection([
        ('=', 'Equal'),
        ('>', 'Greater than'), ('>=', 'Greater than or equal to'), ('ibt', 'In Between'),
        ('<', 'Less Than'), ('<=', 'Less than or equal to')], string='Width Operator')
    thickness_operator = fields.Selection([
        ('=', 'Equal'),
        ('>', 'Greater than'), ('>=', 'Greater than or equal to'), ('ibt', 'In Between'),
        ('<', 'Less Than'), ('<=', 'Less than or equal to')], string='Thickness Operator')

    production_wizard_line_ids = fields.One2many('production.wizard.line', 'production_wizard_id',
                                                 string='Production Wizard Line')

    def pass_to_production(self):

        option_lines = self.production_wizard_line_ids.filtered(lambda l: l.select_line == True)
        if not option_lines:
            raise UserError(_('No Lots are selected'))

        production_object = self.env['steel.production']
        job_object = self.env['job.order']

        job_order_lots = []
        job_order_process = ''
        production_process = ''
        production_lots = []

        for line in option_lines:
            # if self.warehouse_id == line.lot_id.loc_warehouse.id:
            if not line.operation:
                raise UserError(_('Please Select an Operation'))
            if not line.is_job_order:
                production_process = line.operation
                production_lots.append((0, 0, {
                    'lot_id': line.lot_id.id,
                    'product_id': line.product_id.id,
                    'category_id': line.category_id.id,
                    'sub_category_id': line.sub_category_id.id,
                    'product_uom_id': line.uom_id.id,
                    'thickness_in': line.thickness_in,
                    'product_qty': line.lot_id.product_qty,
                    'lot_status': 'in_production',
                    'width_in': line.width_in,
                    'src_warehouse_id': line.lot_id.loc_warehouse.id,

                }))
                line.lot_id.stock_status = 'in_production'

            else:
                # job_order_lots.append(line.lot_id.id)
                job_order_process = line.operation
                job_order_lots.append((0, 0, {
                    'lot_id': line.lot_id.id,
                    'product_id': line.product_id.id,
                    'category_id': line.category_id.id,
                    'sub_category_id': line.sub_category_id.id,
                    'product_uom_id': line.uom_id.id,
                    'thickness_in': line.thickness_in,
                    'product_qty': line.lot_id.product_qty,
                    'lot_status': 'in_production',
                    'width_in': line.width_in,
                    'src_warehouse_id': line.lot_id.loc_warehouse.id,

                }))
                line.lot_id.stock_status = 'in_production'
        if job_order_lots:
            new_job = job_object.create({
                # 'lot_id': line.lot_id.id,
                'sale_line_id': self.sale_line_id.id,
                'operation': job_order_process,
                'description': self.description,
                'sale_order_id': self.sale_order_id.id,
                'job_event_date': fields.Datetime.now(),
                'dest_warehouse_id': self.warehouse_id.id,
                'order_line_product': self.product_id.id,
                'multi_lot_line_ids': job_order_lots
            })

        if production_lots:
            new_production = production_object.create({
                'sale_line_id': self.sale_line_id.id,
                'operation': production_process,
                'sale_order_id': self.sale_order_id.id,
                'dest_warehouse_id': self.warehouse_id.id,
                'order_line_product': self.product_id.id,
                'pro_multi_lot_line_ids': production_lots

                # 'lot_id': line.lot_id.id,
                # 'description': self.description,
                # 'job_event_date': fields.Datetime.now(),
                # 'dest_warehouse_id': self.warehouse_id.id,

                # 'req_width': self.width_in,
                # 'req_thickness': self.thickness_in,
                # 'req_length': self.length_in,
                # 'req_weight': self.weight_lb,
                # 'req_material_type': self.material_type,
            })

            # new_job.write({
            #     'multi_lot_line_ids': [(0, 0, {
            #         'job_order_ref_id': new_job.id,
            #         'lot_id': line.lot_id.id,
            #         'product_id': line.product_id.id,
            #         'category_id': line.category_id.id,
            #         'sub_category_id': line.sub_category_id.id,
            #         'product_uom_id': line.uom_id.id,
            #         'thickness_in': line.thickness_in,
            #         'product_qty': line.lot_id.product_qty,
            #         'lot_status': 'in_production',
            #         'width_in': line.width_in,
            #         'src_warehouse_id': line.lot_id.loc_warehouse.id,
            #         # 'length_in': self.length_in,
            #         # 'material_type': 'coil' if line.operation == 'slitting' or line.operation == 'parting' else 'sheets',
            #         # 'width_in': self.width_in if line.operation == 'slitting' else line.width_in,
            #
            #     })]
            #
            # })

            # new_job.onchange_lot_id()
            # if line.operation == 'slitting' or line.operation == 'cutting':

            # if line.operation == 'slitting':
            #     new_job.job_line_ids._onchange_width_in()
            # if line.operation == 'cutting':
            #     new_job.job_line_ids._onchange_sheets()
            # else:
            #     raise UserError(_('Selected lot is not in the warehouse:  %s' % self.warehouse_id.id))

    def action_search_product(self):
        self.production_wizard_line_ids = False
        domain = [('stock_status', '=', 'available'), ('loc_warehouse', '=', self.warehouse_id.id)]

        if self.production_wizard_line_ids:
            opt_lines = []
            opt_lines = self.production_wizard_line_ids.mapped('lot_id').ids
            domain.append(('id', 'not in', opt_lines))
        if not self.coil_search:
            # if self.product_id:
            #     domain.append(('product_id', '=', self.product_id.id))

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
            domain.append(('name', '=', self.coil_search))

        product_lot = self.env['stock.production.lot'].search(domain)

        if product_lot:
            for rec in product_lot:
                if rec.product_qty > 0:
                    x = self.write({
                        'production_wizard_line_ids': [(0, 0, {
                            'lot_id': rec.id,
                            'product_id': rec.product_id.id,
                            'category_id': rec.product_id.categ_id.parent_id.id,
                            'sub_category_id': rec.product_id.categ_id.id,
                            'weight_lb': rec.product_qty,
                            'uom_id': rec.product_uom_id.id,
                            'thickness_in': rec.thickness_in,
                            'width_in': rec.width_in,
                            'operation': 'slitting' if self.sale_line_id.material_type == 'coil' else 'cutting',

                        })]
                    })

        return {
            'name': _('Production Process'),
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'res_model': 'production.wizard',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',

        }


class ProductionWizardLine(models.TransientModel):
    _name = 'production.wizard.line'

    select_line = fields.Boolean(string="Select")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', 'Sub Product')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    weight_lb = fields.Float(string='Weight(lbs)')
    production_wizard_id = fields.Many2one('production.wizard', string="Production Wizard Ref")
    operation = fields.Selection([
        ('slitting', 'Slitting'),
        ('cutting', 'Cut to Length'),
        ('parting', 'Parting'),
        ('multistage', 'Multi Stage'),
        ('annealing', 'Annealing'),
        ('cr', 'Cold Rolling'),
        ('degreasing', 'DeGreasing'),
        ('tr', 'Temper Rolling'),
        ('pickling', 'Pickling'),
    ], string='Operation', track_visibility="onchange")
    is_job_order = fields.Boolean(string='Job Order')
