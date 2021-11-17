# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_repr

from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        if vals.get('custom_vendor_receipt'):
            vals['vendor_receipt_ref'] = self.env['ir.sequence'].next_by_code('receipt.reference.sequence') or _('New')
        return super(AccountMove, self).create(vals)

    acc_payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')],
                                        string='Payment Type', readonly=True,
                                        states={'draft': [('readonly', False)]})
    acc_payment_amount = fields.Monetary(string='Amount', readonly=True,
                                         states={'draft': [('readonly', False)]},
                                         tracking=True)

    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')], tracking=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    description = fields.Char(string="Description", default="Miscellaneous Payments")
    acc_pay_account_id = fields.Many2one('account.account', string='Account',
                                         index=True, ondelete="restrict", check_company=True,
                                         domain=[('deprecated', '=', False)])
    vendor_receipt_ref = fields.Char('Receipt Reference', default=lambda self: _('New'),
                                     readonly=True)

    acc_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string='Taxes',
        context={'active_test': False},
        help="Taxes that apply on the base amount")

    custom_customer_receipt = fields.Boolean(string="Customer Receipt")
    custom_vendor_receipt = fields.Boolean(string="Vendor Receipt")

    vendor_receipt_status = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Sent For Approval'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Vendor Status', default='draft', copy=False, tracking=True)

    def send_for_approval(self):

        group = self.env.ref('odx_account_receipt_customisation.group_vendor_receipt_approval_access')

        recipients = []
        for recipient in group.users:
            recipients.append(recipient)

        self.ensure_one()

        template_id = self.env.ref('odx_account_receipt_customisation.mail_template_receipt_approver_mail_vendor').id
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_recipient_ids': [(4, x.partner_id.id) for x in recipients],
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        text = template.with_context(ctx)._render_template(html_body, 'account.move', self.id)
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Receipt Approval -%s' % self.vendor_receipt_ref,
            'body_html': text,
        })
        self.message_post(body=text)
        compose.send()
        self.vendor_receipt_status = "approval"

    # def send_for_approval(self):
    #     group = self.env.ref('odx_account_receipt_customisation.group_vendor_receipt_approval_access')
    #
    #     recipients = []
    #     for recipient in group.users:
    #         recipients.append(recipient)
    #
    #     self.ensure_one()
    #     template_id = self.env.ref('odx_account_receipt_customisation.mail_template_receipt_approver_mail_vendor').id
    #     ctx = {
    #         'default_model': 'account.move',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'default_partner_ids': [(4, x.partner_id.id) for x in recipients],
    #     }
    #     template = self.env['mail.template'].browse(template_id)
    #     html_body = template.body_html
    #     text = template.with_context(ctx)._render_template(html_body, 'account.move', self.id)
    #
    #     compose = self.env['mail.compose.message'].with_context(ctx).create({
    #         'subject': 'Receipt Approval -%s' % self.vendor_receipt_ref,
    #         'body': text,
    #     })
    #     compose.action_send_mail()
    #     self.vendor_receipt_status = "approval"
    #
    #
    #     # # lang = self.env.context.get('lang')
    #     # template = self.env['mail.template'].browse(template_id)
    #     # if template:
    #     #     lang = template._render_template(template.body_html, 'account.move', self.ids[0])
    #     #
    #     #     mail_compose = self.env['mail.compose.message'].with_context(
    #     #         {
    #     #             # 'default_composition_mode': 'mass_mail' if len(self.ids) > 1 else 'comment',
    #     #             'default_res_id': self.ids[0],
    #     #             'default_model': 'account.move',
    #     #             'default_use_template': bool(template_id),
    #     #             'default_template_id': template_id,
    #     #             # 'default_subject': self.vendor_receipt_ref,
    #     #             'default_partner_ids': [(4, x.partner_id.id) for x in recipients],
    #     #
    #     #             # 'active_ids': self.ids,
    #     #
    #     #         }).create({
    #     #         'body': lang})
    #     #     print(mail_compose.body,"jj")
    #     #     print(mail_compose.subject,"jj")
    #     #
    #     #
    #     #     mail_compose.action_send_mail()
    #     #     self.vendor_receipt_status = "approval"
    #

    def confirm_custom_receipt(self):
        tax_list = []
        if self.acc_tax_ids:
            for rec in self.acc_tax_ids:
                tax_list.append(rec.id)
        if self.type == 'out_receipt' and self.custom_customer_receipt == True:
            self.with_context(check_move_validity=False).write({
                'invoice_line_ids': [(0, 0, {
                    'name': self.description,
                    'price_unit': self.acc_payment_amount,
                    'tax_ids': [(4, x) for x in tax_list],
                    'account_id': self.journal_id.default_credit_account_id.id,

                })]
            })
            self.action_post()

    def approve_custom_vendor_receipt(self):
        tax_list = []
        if self.acc_tax_ids:
            for rec in self.acc_tax_ids:
                tax_list.append(rec.id)
        if self.type == 'in_receipt' and self.custom_vendor_receipt == True:
            self.with_context(check_move_validity=False).write({
                'invoice_line_ids': [(0, 0, {
                    'name': self.description,
                    'price_unit': self.acc_payment_amount,
                    'tax_ids': [(4, x) for x in tax_list],
                    'account_id': self.journal_id.default_credit_account_id.id,

                })]
            })
            self.action_post()
            self.vendor_receipt_status = 'posted'

    def reject_custom_receipt(self):
        self.button_cancel()
        self.vendor_receipt_status = 'cancel'

    def send_back_custom_receipt(self):
        # self.button_cancel()
        owner = self.create_uid

        self.ensure_one()

        template_id = self.env.ref('odx_account_receipt_customisation.mail_template_sendback_mail_vendor').id
        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_recipient_ids': [(4, owner.partner_id.id)],
        }
        template = self.env['mail.template'].browse(template_id)
        html_body = template.body_html
        text = template.with_context(ctx)._render_template(html_body, 'account.move', self.id)
        compose = self.env['mail.mail'].with_context(ctx).create({
            'subject': 'Receipt Rework -%s' % self.vendor_receipt_ref,
            'body_html': text,
        })
        self.message_post(body=text)
        compose.send()
        self.vendor_receipt_status = 'draft'
