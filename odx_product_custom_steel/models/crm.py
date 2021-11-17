# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    delivery_qty = fields.Integer(compute='_compute_delivery_data', string="Delivery Quantity")


    @api.depends('order_ids.order_line')
    def _compute_delivery_data(self):
        for lead in self:
            delivery_qty = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order_ids:
                qry = ('''select COALESCE(sum(qty_delivered), 0) from sale_order_line where order_id=%s''') %(order.id)
                self.env.cr.execute(qry)
                result = self.env.cr.fetchall()
                if result:
                    delivery_qty += [z[0] for z in result][0]
            lead.delivery_qty = delivery_qty

    def action_view_sale_delivery(self):
        action = self.env.ref('odx_sale_stock_return.odx_action_sale_lines').read()[0]
        action['context'] = {
            'search_default_group_order_id': 1,
            'search_default_group_sub_category_id': 1,
            
        }
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        action['domain'] = [('order_id', 'in', orders.ids)]
        return action