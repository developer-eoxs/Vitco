# -*- coding: utf-8 -*-
# Copyright 2015-2019 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _hold_picking_search(self, operator, value):
        recs = self.env['stock.picking']
        if (operator, value) in [('=', True), ('!=', False)]:
            recs = self.search([]).filtered(lambda x : x.hold_delivery_till_payment is True )
        elif (operator, value) in [('=', False), ('!=', True)]:
            recs = self.search([]).filtered(lambda x : x.hold_delivery_till_payment is False )
        return [('id', 'in', recs.ids)]

    hold_delivery_till_payment = fields.Boolean(default= False, copy= False, compute="_check_delivery_hold", string="Hold Delivery", help="If True, then holds the DO until  \
                                    invoices are paid and equals to the total amount on the SO", search=_hold_picking_search)

    def button_validate(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                return picking.show_do_hold_warning()
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).button_validate()

    def action_confirm(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                if picking._context.get('hold_do'):
                    return picking.show_do_hold_warning()
                else:
                    return
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).action_confirm()

    def action_assign(self):
        for picking in self:
            partner = picking.partner_id.commercial_partner_id
            if picking.hold_delivery_till_payment:
                return
            if partner.credit_hold and not self._context.get('website_order_tx', False):
                raise UserError(
                    _('Credit Hold!\n\nThis customer is on Credit hold.'))
        return super(StockPicking, self).action_assign()

    def _check_delivery_hold(self):
        for picking in self:
            if picking.sale_id.hold_delivery_till_payment and not picking.sale_id.check_invoice_fully_paid():
                picking.hold_delivery_till_payment = True
            else:
                picking.hold_delivery_till_payment = False

    def show_do_hold_warning(self):
        """Raise user warning if the invoice(s) is/are not fully paid."""
        raise UserError(_("Delivery is on hold."))

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def _get_moves_to_assign_domain(self, company_id):
        """ This method adds hold delivery domain to restrict while checking
        availability during the scheduler run"""
        domain = super(ProcurementGroup, self)._get_moves_to_assign_domain(company_id)
        domain = expression.AND([domain, [('picking_id.hold_delivery_till_payment', '!=', True)]])
        return domain
