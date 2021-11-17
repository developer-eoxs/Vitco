# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    state = fields.Selection([
            ('draft', 'Quote'),
            ('sent', 'Quote Sent'),
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
            ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Quote Template',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    name = fields.Char('Quote Template', required=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_sale_order_template = fields.Boolean("Quote Templates", implied_group='sale_management.group_sale_order_template')
    module_sale_quotation_builder = fields.Boolean("Quote Builder")
