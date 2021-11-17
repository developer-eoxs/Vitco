# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    so_approval = fields.Boolean(string="So Approval",default=True)
    double_validation_amt = fields.Float(string="Double validation Amount",default=10000.00)

    @api.model
    def get_values(self):
        res = super(ConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        so_approval = params.get_param('so_approval',default=True)
        res.update(so_approval=so_approval)
        res.update(double_validation_amt=literal_eval(params.get_param('double_validation_amt','10000')))
        return res

    def set_values(self):
        super(ConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "so_approval",
            self.so_approval)
        self.env['ir.config_parameter'].sudo().set_param(
            "double_validation_amt",
            self.double_validation_amt)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_view_sale_history(self):
        action = self.env.ref('odx_steel_customisation.action_odx_sale_history').read()[0]
        action['context'] = {
            'search_default_product_id_gr': 1,
        }
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        return action

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('to_approve', 'To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_confirm(self):
        res_config = self.env['res.config.settings'].search([])
        settings_partner = self.env['ir.config_parameter'].sudo().get_param('odx_steel_customisation.so_approval')
        params = self.env['ir.config_parameter'].sudo()
        so_approval = params.get_param('so_approval')
        double_validation_amt = literal_eval(params.get_param('double_validation_amt',default=10000))
        if so_approval and float(double_validation_amt) < self.amount_total and self.state != 'to_approve':
            self.write({
                'state': 'to_approve',
            })   
        else :
            res = super(SaleOrder,self).action_confirm()
            return res

    def to_approved(self):
        print 
        if self.env.user.has_group('sales_team.group_sale_manager'):
            self.action_confirm()
        else:
            raise ValidationError(_('Only Manager Can Approve.'))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    markup = fields.Float(string="Markup")
    break_id = fields.Many2one('odx.break.point',string="Breakpoint")

    @api.onchange('markup')
    def product_markup_change(self):
        # product = self.product_id.with_context(
        #         lang=self.order_id.partner_id.lang,
        #         partner=self.order_id.partner_id,
        #         quantity=self.product_uom_qty,
        #         date=self.order_id.date_order,
        #         pricelist=self.order_id.pricelist_id.id,
        #         uom=self.product_uom.id,
        #         fiscal_position=self.env.context.get('fiscal_position')
        #     )
        # price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        # self.price_unit = self.product_id.standard_price*self.markup
        self.price_unit = self.purchase_price*self.markup
        # price = self._get_display_price(self.product_id)
        # self.price_unit = price*self.markup
        # self.price_unit = price_unit*self.markup
        # self.price_unit = self.purchase_price*self.markup


    # @api.onchange('price_unit')
    def product_price_unit_change(self):
        markup=0
        if self.price_unit and self.product_id.standard_price!=0:
            markup = self.price_unit/self.product_id.standard_price
        self.markup = markup
        return markup

    # def write(self,values):
    #     result = super(SaleOrderLine, self).write(values)
    #     if 'price_unit' in values:
    #         self.product_price_unit_change()
    #     return result

    # @api.model_create_multi
    # def create(self, vals_list):
    #     result = super(SaleOrderLine, self).create(vals_list)
    #     for values in vals_list:
    #         if 'price_unit' in values:
    #             result.markup = result.product_price_unit_change()
    #     return result

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine,self).product_id_change()
        # update cost in unit price
        self.update({'price_unit':self.purchase_price})
        if self.markup!=0:
            self.markup=0
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine,self).product_uom_change()
        self.update({'price_unit':self.purchase_price})
        return res

    def generate_breakpoint(self):
        if not self.break_id:
            if self.markup==0:
                raise ValidationError(_('Please Add Markup.!!'))

            breakpoint_object = self.env['odx.break.point']
            vals = {
                'sale_line_id': self.id,
                'product_id': self.product_id.id,
                'name': self.name,
                'line_ids': []
            }
            vals['line_ids'].append((0, 0, {
                'name': 'Material',
                'cost': self.purchase_price,
                # 'cost': self.price_unit /self.markup,
                'markup': self.markup,
                'price': self.price_unit,
                # 'price': self.price_unit,
            }))
            new_breakpoint = breakpoint_object.create(vals)
            self.break_id = new_breakpoint.id
        
        return {
            'name': 'Pricing Breakpoint',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'odx.break.point',
            'view_id': False,
            'target': 'current',
            'res_id': self.break_id.id,
            'type': 'ir.actions.act_window',
        }