from odoo import models, fields, api, _
from odoo.exceptions import UserError

from odoo.tools import float_round


class ProductionInstructions(models.Model):
    _name = 'production.instructions'
    _description = 'Production Instructions'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('production.instruction.sequence') or _('New')
        return super(ProductionInstructions, self).create(vals)

    date = fields.Date(string="Creation Date", default=fields.Date.today)
    due_date = fields.Date(string="Due Date")
    name = fields.Char(string="WO #")

    number_of_productions = fields.Integer(string="No. of Productions")
    run_line_ids = fields.One2many('instructions.run.line', 'prod_inst_ref_id', string="Instruction Line")
    production_id = fields.Many2one('steel.production', string='Production')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'In Production'),
        ('produced', 'Produced'),
    ], string='State', default='draft')
    production_count = fields.Integer(string="Count", compute="_compute_production_count")
    scrap_percent = fields.Float(string="Scrap %", compute='total_scrap_percent')
    warning_message = fields.Char(string='Warning', readonly=True, compute='show_warning_message')

    def total_scrap_percent(self):
        for rec in self:
            rec.scrap_percent = 0
            total_wt = 0
            scrap_wt = 0
            i = 0
            for tag in rec.run_line_ids:
                if i < 1:
                    total_wt = sum(tag.mapped('instruction_run_line_ids').mapped('product_qty'))
                    i += 1
            scrap_wt = sum(rec.mapped('run_line_ids').mapped('total_scrap_wt'))
            if total_wt and scrap_wt:
                rec.scrap_percent = (scrap_wt / total_wt) * 100

    def add_number_of_runs(self):
        if self.number_of_productions:
            # self.run_line_ids = False
            i = 1
            while i <= self.number_of_productions:
                # run_name = ''
                # run_name = "PR" + str(i)
                self.write({
                    'run_line_ids': [(0, 0, {
                        'name': _('New'),
                        # 'lot_id': self.lot_id.id,
                    })]
                })
                i += 1

    def confirm_prd(self):
        if self.run_line_ids:
            prepare_scheduler_line = []
            check_machine = []
            for rec in self.run_line_ids:
                set_ready_state = False
                if not rec.send_for_production:
                    raise UserError(_("Please create production for %s" % rec.name))
                if rec.machine_id.id not in check_machine:
                    check_machine.append(rec.machine_id.id)
                    set_ready_state = True

                if set_ready_state:
                    state = 'ready'
                else:
                    state = 'pending'

                next_pr_run_id = self.env['instructions.run.line'].search([
                    ('id', '>', rec.id),
                    ('prod_inst_ref_id', '=', self.id)], limit=1)

                prepare_scheduler_line.append({
                    'machine_id': rec.machine_id.id,
                    'work_order_id': self.id,
                    'pr_run_id': rec.id,
                    'due_date': self.due_date,
                    'state': state,
                    'next_pr_run_id': next_pr_run_id.id or False,
                })
            self.state = 'done'
            machine_schedular_obj = self.env['machine.scheduler']
            for line in prepare_scheduler_line:
                machine_schedular_obj.create(line)

    def _compute_production_count(self):
        lines = []
        if self.run_line_ids:
            lines = self.mapped('run_line_ids').mapped('production_ids')
        self.production_count = len(lines)

    def action_view_production(self):
        lines = []
        if self.run_line_ids:
            lines = self.mapped('run_line_ids')
        return {
            'name': _('Productions'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'steel.production',
            'view_id': False,
            'domain': [('instruction_line_id', 'in', lines.ids)],
        }
        # 'context': {
        #     'search_default_sale_line_id': 'sale_line_id'
        #     # 'search_default_sale_line_id': 1,
        #     # 'default_group_by_sale_line_id': 1
        # }

    def show_warning_message(self):
        for rec in self:
            if rec.scrap_percent > 3:
                rec.warning_message = _(
                    "Total scrap percentage exceeded the scrap limit")
            else:
                rec.warning_message = False


class InstructionsRunLine(models.Model):
    _name = 'instructions.run.line'
    _description = 'Instructions Line'
    _order = "id asc"

    @api.model
    def default_get(self, fields):
        rec = super(InstructionsRunLine, self).default_get(fields)
        if not self.env.context.get('default_prod_inst_ref_id'):
            raise UserError(_("Please Save the Work Order details!"))
        rec['prod_inst_ref_id'] = self.env.context.get('default_prod_inst_ref_id')
        return rec

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('production.run.sequence') or _('New')
        return super(InstructionsRunLine, self).create(vals)

    name = fields.Char(string='PR No.')
    instruction_run_line_ids = fields.One2many('production.instructions.tag', 'instruction_line_id',
                                               string="Instruction Line")
    tag_line_ids = fields.One2many('production.instructions.tag.line', 'instruction_ref_line_id',
                                   string="Instruction Line")
    prod_inst_ref_id = fields.Many2one('production.instructions', string='Instructions Ref')
    production_ref_id = fields.Many2one('steel.production', string='Production Id')
    rolled_coil_thickness = fields.Char(string='Thk on Re-rolling')
    send_for_production = fields.Boolean(string='Send For Production', default=False, copy=False)
    operation = fields.Selection([
        ('slitting', 'Slitting'),
        ('cutting', 'Cut to Length'),
        ('parting', 'Re-Winding'),
    ], string='Operation', required=True, default='slitting')
    production_ids = fields.One2many('steel.production', 'instruction_line_id', string='Production Orders')
    machine_id = fields.Many2one('production.machine', string='Machine')
    scrap_percent = fields.Float(string='Scrap %', compute='calculate_scrap_percent')
    total_scrap_wt = fields.Float(string='Scrap Weight', compute='calculate_scrap_weight')
    pr_instructions = fields.Html(string='Instructions')
    warning_message = fields.Char(string='Warning', readonly=True, compute='show_warning_message')
    finish_picking_id = fields.Many2one('stock.picking', 'Finish Picking')

    def show_warning_message(self):
        for rec in self:
            if rec.scrap_percent > 3:
                rec.warning_message = _(
                    "Total scrap percentage exceeded the scrap limit")
            else:
                rec.warning_message = False

    def add_scrap_line(self):
        if self.operation == 'cutting':
            for tags in self.instruction_run_line_ids:
                balance_wt = balance_width = 0
                line_weight = 0
                line_width = 0
                for lines in self.tag_line_ids:
                    if tags.lot_id == lines.lot_id:
                        line_weight += lines.product_qty
                        # line_width += lines.width_in

                balance_wt = tags.product_qty - line_weight
                # balance_width = tags.width_in - line_width
                if line_weight < tags.product_qty:
                    self.write({
                        'tag_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': tags.product_id.id,
                            'category_id': tags.category_id.id,
                            'sub_category_id': tags.sub_category_id.id,
                            'product_qty': balance_wt,
                            'width_in': tags.width_in,
                            'product_uom_id': tags.product_uom_id.id,
                            'thickness_in': tags.thickness_in,
                            # 'lot_status': 'available',
                            'material_type': 'sheets',
                            'is_scrap': True,

                        })]
                    })
        if self.operation == 'parting':
            for tags in self.instruction_run_line_ids:
                balance_wt = balance_width = 0
                line_weight = 0
                line_width = 0
                for lines in self.tag_line_ids:
                    if tags.lot_id == lines.lot_id:
                        line_weight += lines.product_qty
                        # line_width += lines.width_in

                balance_wt = tags.product_qty - line_weight
                # balance_width = tags.width_in - line_width
                if line_weight < tags.product_qty:
                    self.write({
                        'tag_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': tags.product_id.id,
                            'category_id': tags.category_id.id,
                            'sub_category_id': tags.sub_category_id.id,
                            'product_qty': balance_wt,
                            'width_in': tags.width_in,
                            'product_uom_id': tags.product_uom_id.id,
                            'thickness_in': tags.thickness_in,
                            # 'lot_status': 'available',
                            'material_type': 'sheets',
                            'is_scrap': True,

                        })]
                    })

        if self.operation == 'slitting':
            for tags in self.instruction_run_line_ids:
                balance_wt = balance_width = 0
                line_weight = 0
                line_width = 0
                for lines in self.tag_line_ids:
                    if tags.lot_id == lines.lot_id:
                        line_weight += lines.product_qty
                        line_width += lines.width_in

                balance_wt = tags.product_qty - line_weight
                balance_width = tags.width_in - line_width
                if line_weight < tags.product_qty:
                    self.write({
                        'tag_line_ids': [(0, 0, {
                            'lot_id': tags.lot_id.id,
                            'product_id': tags.product_id.id,
                            'category_id': tags.category_id.id,
                            'sub_category_id': tags.sub_category_id.id,
                            'product_qty': balance_wt,
                            'width_in': balance_width,
                            'product_uom_id': tags.product_uom_id.id,
                            'thickness_in': tags.thickness_in,
                            # 'lot_status': 'available',
                            'material_type': 'sheets',
                            'is_scrap': True,

                        })]
                    })

    def calculate_scrap_percent(self):
        for rec in self:
            rec.scrap_percent = 0
            lot_wt = 0
            scrap_wt = 0
            for tag in rec.instruction_run_line_ids:
                lot_wt += tag.product_qty
            for line in rec.tag_line_ids:
                if line.is_scrap:
                    scrap_wt += line.product_qty
            if lot_wt and scrap_wt:
                rec.scrap_percent = (scrap_wt / lot_wt) * 100

    def calculate_scrap_weight(self):
        for rec in self:
            rec.total_scrap_wt = 0
            lot_wt = 0
            scrap_wt = 0
            for line in rec.tag_line_ids:
                if line.is_scrap:
                    scrap_wt += line.product_qty
            if scrap_wt:
                rec.total_scrap_wt = scrap_wt

    def update_instruction_run_line(self):
        self.save_form()
        self.tag_line_ids.unlink()
        for instruction_run_line_id in self.instruction_run_line_ids:
            instruction_run_line_id.update_lines()

    def save_form(self):
        # self.write(vals)
        # self.prod_inst_ref_id.write()
        # self.env.cr.commit()
        return self.id
        # self.prod_inst_ref_id.env.cr.commit()
        # return {
        #     'name': _('Import CRD'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'instructions.run.line',
        #     'res_id': self.id,
        #     # 'target': 'new',
        #     # 'views': [(False, 'form')],
        #     # 'view_id': False,
        # }

    def create_production(self):
        production_obj = self.env['steel.production']
        company = self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        production_lots = []
        if not self.send_for_production:
            for source_tag in self.instruction_run_line_ids:
                line_width = line_weight = residue_width = residue_weight = 0
                for line_tag in self.tag_line_ids:
                    if line_tag.lot_id == source_tag.lot_id:
                        # line_width += line_tag.width_in
                        line_weight += line_tag.product_qty

                # if line_width > source_tag.width_in:
                #     raise UserError(_("Sum of the widths exceeded the Coil Width for %s" % source_tag.lot_id.name))
                if line_weight > source_tag.product_qty:
                    raise UserError(_("Sum of the weights exceeded the Coil Weight for %s" % source_tag.lot_id.name))

            if self.instruction_run_line_ids:
                for rec in self.instruction_run_line_ids:
                    production_lots.append((0, 0, {
                        'lot_id': rec.lot_id.id,
                        'product_id': rec.lot_id.product_id.id,
                        'category_id': rec.lot_id.category_id.id,
                        'sub_category_id': rec.lot_id.sub_category_id.id,
                        'product_uom_id': rec.lot_id.product_uom_id.id,
                        'thickness_in': rec.lot_id.thickness_in,
                        'product_qty': rec.lot_id.product_qty,
                        'lot_status': 'available',
                        'width_in': rec.lot_id.width_in,
                        'src_warehouse_id': rec.lot_id.loc_warehouse.id,
                        'number_of_slits': rec.no_of_slits,
                        'number_of_bundles': rec.no_of_bundles,

                    }))
            if self.tag_line_ids:
                production_line_list = []
                for line in self.tag_line_ids:
                    production_line_list.append((0, 0, {
                        'lot_id': line.lot_id.id,
                        'product_id': line.lot_id.product_id.id,
                        'category_id': line.lot_id.category_id.id,
                        'sub_category_id': line.lot_id.sub_category_id.id,
                        'product_uom_id': line.lot_id.product_uom_id.id,
                        'thickness_in': line.lot_id.thickness_in,
                        'product_qty': line.product_qty,
                        'width_in': line.width_in,
                        'length_in': line.length_in,
                        'number_of_sheets': line.number_of_sheets,
                        'is_scrap': line.is_scrap,
                        'material_type': line.material_type,
                        # 'remarks': line.remarks,
                        # 'src_warehouse_id': self.lot_id.loc_warehouse.id,
                    }))
                if production_line_list:
                    new_production = self.env['steel.production'].create({
                        'operation': self.operation,
                        'dest_warehouse_id': warehouse.id,
                        'pro_multi_lot_line_ids': production_lots,
                        'production_line_ids': production_line_list,
                        'instruction_line_id': self.id,
                    })
                    if new_production:
                        self.production_ref_id = new_production.id
                        self.send_for_production = True
                        return {
                            'name': _('Production Confirmed'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'production.instructions',
                            'views': [(False, 'form')],
                            'view_id': False,
                            'res_id': self.prod_inst_ref_id.id,
                            # 'res_model': 'production.confirm.wizard',
                            # 'context': {
                            #     'default_instruction_line_id': self.id,
                            # }
                        }
        raise UserError(_("A Production is already generated"))

    def create_picking(self):
        # if self.instruction_run_line_ids:
        #     if self.operation == 'slitting' or self.operation == 'parting':
        #         for source_tag in self.instruction_run_line_ids:
        #             line_width = line_weight = residue_width = residue_weight = 0
        #             for line_tag in self.tag_line_ids:
        #                 if line_tag.lot_id == source_tag.lot_id:
        #                     line_width += line_tag.width_in
        #                     line_weight += line_tag.product_qty
        #
        #             if line_width > source_tag.width_in:
        #                 raise UserError(_("Sum of the widths exceeded the Coil Width for %s" % source_tag.lot_id.name))
        #             if line_weight > source_tag.product_qty:
        #                 raise UserError(_("Sum of the weights exceeded the Coil Weight for %s" % source_tag.lot_id.name))
        #
        #     if self.operation == 'cutting':
        #         for source_tag in self.instruction_run_line_ids:
        #             line_width = line_weight = residue_width = residue_weight = 0
        #             for line_tag in self.tag_line_ids:
        #                 if line_tag.lot_id == source_tag.lot_id:
        #                     # line_width += line_tag.width_in
        #                     line_weight += line_tag.product_qty
        #
        #             # if line_width > source_tag.width_in:
        #             #     raise UserError(_("Sum of the widths exceeded the Coil Width for %s" % source_tag.lot_id.name))
        #             if line_weight > source_tag.product_qty:
        #                 raise UserError(
        #                     _("Sum of the weights exceeded the Coil Weight for %s" % source_tag.lot_id.name))

        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id)])
        production_location = self.env['stock.location'].search([('usage', '=', 'production'),
                                                                 ('company_id', '=', self.env.company.id)],
                                                                limit=1)
        company = self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)

        dest_wh_location = self.env.ref('stock.stock_location_stock').id
        dest_wh = self.env['stock.warehouse'].search([('lot_stock_id', '=', dest_wh_location)])

        dest_picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
             ('warehouse_id', '=', warehouse.id)])

        self.add_scrap_line()
        for lots in self.instruction_run_line_ids:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'), ('company_id', '=', self.env.company.id),
                 ('warehouse_id', '=', lots.src_warehouse_id.id)])

            picking_source_id = self.env['stock.picking'].create({
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
                'picking_type_id': picking_type.id,
                'company_id': self.env.company.id,
            })

            move = self.env['stock.move'].create({
                'name': lots.product_id.name,
                'product_id': lots.product_id.id,
                'product_uom_qty': lots.product_qty,
                'product_uom': lots.product_uom_id.id,
                'picking_id': picking_source_id.id,
                'location_id': lots.src_warehouse_id.lot_stock_id.id,
                'location_dest_id': production_location.id,
            })
            move_line_id = self.env['stock.move.line'].create(move._prepare_move_line_vals())

            for line in move_line_id:
                line.lot_id = lots.lot_id.id
                line.lot_name = lots.lot_id.name
                line.qty_done = lots.product_qty
            picking_source_id.button_validate()

            lots.lot_id.stock_status = 'not_available'
            lots.lot_status = 'not_available'
            lots.lot_id.process_done = self.operation
            # if self.operation == 'annealing':
            #     lots.lot_id.is_annealed = 'yes'

        if self.tag_line_ids:
            product = []
            for line in self.tag_line_ids:
                if not line.is_scrap:
                    product.append(line)
            finished_picking = self.env['stock.picking'].create({
                'location_id': production_location.id,
                'location_dest_id': dest_wh_location,
                'picking_type_id': dest_picking_type.id,
                'company_id': self.env.company.id,
            })

            for products in product:
                move_lines_list = []
                new_move_list = []
                status_stock = ''
                i = bundle_quantity = 0
                sheet_numbers = 0

                if products.product_qty:
                    move = self.env['stock.move'].create({
                        'name': products.product_id.name,
                        'product_id': products.product_id.id,
                        'product_uom_qty': products.product_qty,
                        'product_uom': products.product_uom_id.id,
                        'picking_id': finished_picking.id,
                        'location_id': production_location.id,
                        'location_dest_id': dest_wh_location,
                        # 'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                    })
                lot_ids = []
                rounding = products.product_uom_id.rounding
                qty = float_round(products.product_qty, precision_rounding=rounding)

                status_stock = 'available'

                new_lots = self.env['stock.production.lot'].with_context({'baby_lot': True}). \
                    create(
                    {'name': _('New'),
                     'product_id': products.product_id.id,
                     'company_id': self.env.company.id,
                     'sub_category_id': products.product_id.categ_id.id,
                     'category_id': products.product_id.categ_id.parent_id.id,
                     'product_qty': qty,
                     'weight_lb': products.product_qty,
                     'product_uom_id': products.product_uom_id.id,
                     'thickness_in': products.thickness_in,
                     'width_in': products.width_in,
                     'length_in': products.length_in if products.material_type == 'sheets' else 0,
                     'material_type': products.material_type,
                     'number_of_sheets': products.number_of_sheets if products.material_type == 'sheets' else 0,
                     'is_child_coil': True,
                     'parent_coil_id': products.lot_id.id,
                     'stock_status': status_stock,
                     'bill_of_lading': products.lot_id.bill_of_lading,
                     'vendor_id': products.lot_id.vendor_id.id if products.lot_id.vendor_id else False,
                     # 'vendor_location_id': products.lot_id.vendor_location_id.id if products.lot_id.vendor_location_id else False,
                     'vendor_serial_number': products.lot_id.vendor_serial_number,
                     'thickness_spec': products.lot_id.thickness_spec,
                     'rockwell': products.lot_id.rockwell,
                     'yield_mpa': products.lot_id.yield_mpa,
                     'elongation': products.lot_id.elongation,
                     'tensile_mpa': products.lot_id.tensile_mpa,
                     'date_received': products.lot_id.date_received,

                     'internet_serial': products.lot_id.internet_serial,
                     'packing_slip_no': products.lot_id.packing_slip_no,
                     'comp_c': products.lot_id.comp_c,
                     'comp_mn': products.lot_id.comp_mn,
                     'comp_p': products.lot_id.comp_p,
                     'comp_s': products.lot_id.comp_s,
                     'comp_si': products.lot_id.comp_si,
                     'comp_al': products.lot_id.comp_al,
                     'comp_cr': products.lot_id.comp_cr,
                     'comp_nb': products.lot_id.comp_nb,
                     'comp_ti': products.lot_id.comp_ti,
                     'comp_ca': products.lot_id.comp_ca,
                     'comp_n': products.lot_id.comp_n,
                     'comp_ni': products.lot_id.comp_ni,
                     'comp_cu': products.lot_id.comp_cu,
                     'comp_v': products.lot_id.comp_v,
                     'comp_b': products.lot_id.comp_b,
                     'pass_oil': products.lot_id.pass_oil,
                     'finish': products.lot_id.finish,
                     'temper': products.lot_id.temper,
                     'category': products.lot_id.category,
                     'coating': products.lot_id.coating,
                     'heat_number': products.lot_id.heat_number,
                     'lift_number': products.lot_id.lift_number,
                     'part_number': products.lot_id.part_number,
                     'tag_number': products.lot_id.tag_number,
                     'grade': products.lot_id.grade,
                     'quality': products.lot_id.quality,
                     # 'loc_city': self.dest_warehouse_id.lot_stock_id.id,
                     # 'loc_warehouse': self.dest_warehouse_id.id,
                     'loc_city': self.env.ref('stock.stock_location_stock').id,
                     'loc_warehouse': warehouse.id,
                     'po_number': products.lot_id.po_number,
                     # 'is_annealed': 'yes' if self.operation == 'annealing' else 'no',
                     'is_annealed': 'no',
                     'purchase_cost': products.lot_id.purchase_cost + products.lot_id.landed_cost,
                     'total_purcahse_cost': (products.lot_id.purchase_cost + products.lot_id.landed_cost) * qty,

                     })
                new_lots._onchange_width()
                new_lots._onchange_thickness()
                new_lots._onchange_length()
                lot_ids.append(new_lots)
                products.finished_lot_id = new_lots.id
                if products.action == "restock":
                    line_status = 'available'
                elif products.action == "reslit":
                    line_status = 'in_production'
                elif products.action == "finished_goods":
                    line_status = 'finished_good'
                else:
                    line_status = 'available'

                products.lot_status = line_status
                move_line_id = self.env['stock.move.line'].create(
                    move._prepare_move_line_vals())

                for line in move_line_id:
                    line.lot_id = new_lots.id
                    line.qty_done = qty
                    new_move_list = line.id

            # try:
            #     finished_picking.action_confirm()
            # except:
            #     pass
            # finished_picking.with_context({'baby_lot': True}).button_validate()
            self.finish_picking_id = finished_picking.id
            self.send_for_production = True
            # self.write({'state': 'done'})
            # return {'type': 'ir.actions.client', 'tag': 'reload'}


class ProductionInstructionsTag(models.Model):
    _name = 'production.instructions.tag'
    _description = 'Production Instructions Tag'

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Lot",
                             domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available'), ])
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Weight')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    tagline_ref_id = fields.Many2one('production.instructions.tag.line', string='Tag Line Ref')
    instruction_line_id = fields.Many2one('instructions.run.line', string='Instruction Line Ref')
    no_of_slits = fields.Integer(string="No. of Slits")
    no_of_bundles = fields.Integer(string="No. of Bundles")
    no_of_parts = fields.Integer(string="No. of Parts")
    src_warehouse_id = fields.Many2one('stock.warehouse', 'Source WH', required=True)
    lot_status = fields.Selection([
        ('transit', 'In Transit'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('not_available', 'Not available')
    ], string='Stock Status')

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.category_id = self.lot_id.category_id.id if self.lot_id.category_id else False
        self.sub_category_id = self.lot_id.sub_category_id.id if self.lot_id.sub_category_id else False
        self.product_id = self.lot_id.product_id.id if self.lot_id.product_id else False
        self.product_qty = self.lot_id.product_qty / self.lot_id.no_of_pieces if self.lot_id.no_of_pieces else self.lot_id.product_qty
        self.width_in = self.lot_id.width_in
        self.thickness_in = self.lot_id.thickness_in
        self.product_uom_id = self.lot_id.product_uom_id.id if self.lot_id.product_uom_id else False
        self.lot_status = self.lot_id.stock_status
        self.src_warehouse_id = self.lot_id.loc_warehouse.id

    def update_lines(self):
        i = 0
        if self.lot_id:
            if self.instruction_line_id.operation == 'slitting':
                if self.no_of_slits > 0:
                    while i < self.no_of_slits:
                        self.instruction_line_id.write({
                            'tag_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'category_id': self.lot_id.category_id.id,
                                'sub_category_id': self.lot_id.sub_category_id.id,
                                'product_id': self.lot_id.product_id.id,
                                'product_uom_id': self.lot_id.product_uom_id.id,
                                'thickness_in': self.lot_id.thickness_in,
                                'width_in': self.width_in / self.no_of_slits,
                                'product_qty': int(self.product_qty / self.no_of_slits),
                                'material_type': 'coil',
                            })]
                        })
                        i += 1
            if self.instruction_line_id.operation == 'cutting':
                if self.no_of_bundles > 0:
                    while i < self.no_of_bundles:
                        self.instruction_line_id.write({
                            'tag_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'category_id': self.lot_id.category_id.id,
                                'sub_category_id': self.lot_id.sub_category_id.id,
                                'product_id': self.lot_id.product_id.id,
                                'product_uom_id': self.lot_id.product_uom_id.id,
                                'thickness_in': self.lot_id.thickness_in,
                                'width_in': self.width_in,
                                # 'product_qty': int(self.product_qty / self.no_of_slits),
                                'material_type': 'sheets',
                            })]
                        })
                        i += 1
            if self.instruction_line_id.operation == 'parting':
                if self.no_of_parts > 0:
                    while i < self.no_of_parts:
                        self.instruction_line_id.write({
                            'tag_line_ids': [(0, 0, {
                                'lot_id': self.lot_id.id,
                                'category_id': self.lot_id.category_id.id,
                                'sub_category_id': self.lot_id.sub_category_id.id,
                                'product_id': self.lot_id.product_id.id,
                                'product_uom_id': self.lot_id.product_uom_id.id,
                                'thickness_in': self.lot_id.thickness_in,
                                'width_in': self.width_in,
                                'product_qty': int(self.product_qty / self.no_of_parts),
                                'material_type': 'coil',
                            })]
                        })
                        i += 1


class ProductionInstructionsTagLine(models.Model):
    _name = 'production.instructions.tag.line'
    _description = 'Production Instructions TagLine'

    lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Parent Coil",
                             domain=[('material_type', '=', 'coil'), ('stock_status', '=', 'available'), ])
    finished_lot_id = fields.Many2one(comodel_name='stock.production.lot', string="Lot", )
    category_id = fields.Many2one('product.category', string="Master", domain="[('parent_id', '=', False)]")
    sub_category_id = fields.Many2one('product.category', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Weight')
    width_in = fields.Float(string='Width(in)', digits=[6, 4])
    number_of_sheets = fields.Integer(string='Sheets')
    length_in = fields.Float(string='Length(in)', digits=[8, 4])
    thickness_in = fields.Float(string='Thickness(in)', digits=[6, 4])
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    instruction_ref_line_id = fields.Many2one('instructions.run.line', string='Instructions Ref')
    # instruction_tag_ref = fields.Many2one('production.instructions.tag', string='Instructions Tag Ref')
    # inst_ref_id = fields.Many2one('production.instructions', string='Instructions Ref')
    is_scrap = fields.Boolean(string='Scrap Weight', default=False, copy=False)
    sale_order_id = fields.Many2one('sale.order', string='SO', copy=False,
                                    domain="[('state', '=', 'draft')]")
    order_line_id = fields.Many2one('sale.order.line', string='OrderLine', copy=False,
                                    domain="[('order_id', '=', sale_order_id) or [] ]")
    so_line_updated = fields.Boolean('Orderline Updated')
    material_type = fields.Selection([
        ('coil', 'Coil'),
        ('sheets', 'Sheets'),
    ], string='Material Type')
    action = fields.Selection([
        ('restock', 'Restock'),
        ('reslit', 'Re-Run'),
        ('finished_goods', 'Finished Goods'),
    ], string='Action')
    lot_status = fields.Selection([
        ('transit', 'In Transit'),
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('in_production', 'In production'),
        ('finished_good', 'Finished Good'),
        ('not_available', 'Not available')
    ], string='Status')

    @api.onchange('width_in')
    def _onchange_width_in(self):
        coil_weight = 0
        coil_width = 0
        unit_weight = 0
        if self.width_in:
            coil_weight = self.lot_id.product_qty
            coil_width = self.lot_id.width_in
            unit_weight = (coil_weight / coil_width)
            self.product_qty = int(unit_weight * self.width_in)

    @api.onchange('width_in', 'length_in', 'number_of_sheets')
    def _onchange_sheets(self):
        if self.material_type == 'sheets':
            coil_weight = coil_width = unit_sheet_weight = 0
            print(self.thickness_in, self.width_in, "klk")
            unit_sheet_weight = self.thickness_in * self.width_in * self.length_in * 0.284
            self.product_qty = int(unit_sheet_weight * self.number_of_sheets)

    def add_to_sale_order(self):
        if self.sale_order_id:
            if self.order_line_id:
                self.order_line_id.write({
                    'lot_id': self.finished_lot_id.id,
                    'category_id': self.finished_lot_id.category_id.id,
                    'sub_category_id': self.finished_lot_id.sub_category_id.id,
                    'product_id': self.finished_lot_id.product_id.id,
                    'product_uom': self.finished_lot_id.product_uom_id.id,
                    'thickness_in': self.finished_lot_id.thickness_in,
                    'width_in': self.width_in,
                    'length_in': self.length_in,
                    'product_uom_qty': self.finished_lot_id.product_qty,
                    'material_type': self.material_type,
                })
                self.so_line_updated = True
            else:
                self.sale_order_id.sudo().write({
                    'order_line': [(0, 0, {
                        'order_id': self.order_line_id.id,
                        'lot_id': self.finished_lot_id.id,
                        'product_id': self.finished_lot_id.product_id.id,
                        'category_id': self.finished_lot_id.category_id.id,
                        'sub_category_id': self.finished_lot_id.sub_category_id.id,
                        'product_uom_qty': self.finished_lot_id.product_qty,
                        'product_uom': self.finished_lot_id.product_uom_id.id,
                        'thickness_in': self.thickness_in,
                        'width_in': self.width_in,
                        'length_in': self.length_in,
                        'material_type': self.material_type
                    })]
                })
                self.so_line_updated = True

    # def unlink(self):
    #     res = super(ProductionInstructionsTagLine, self).unlink()
    #     if self.instruction_ref_line_id.send_for_production:
    #         raise UserError(_("Unable to delete since Production is generated for the line"))
    #     return res
