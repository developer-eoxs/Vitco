from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    print_count = fields.Integer(string="Print Count", copy=False)

    # def new_orders_notify(self):
    #     for record in self:
    #         admin_user = self.env['res.users'].browse(SUPERUSER_ID)
    #         MailThread = self.env['mail.thread']
    #         recievers = []
    #         if record.company_id.msg_users_id:
    #             for user in record.company_id.msg_users_id:
    #                 recievers.append(user)
    #             mail_vals = {}
    #             notification_ids = []
    #             for reciever in recievers:
    #                 email_from = admin_user.login
    #                 subject = 'New Orders has been placed!'
    #                 message = """
    #                                                         <html>
    #                                                             <head>
    #                                                                 Dear %s,
    #                                                             </head>
    #                                                             <body style="">
    #                                                                 New order (<a role="button" href=# data-oe-model=sale.order data-oe-id=%d>%s</a>) placed.</br>
    #                                                                 <strong>Order Details</strong></br>
    #                                                                 Date: %s</br>
    #                                                                 Customer name: %s</br>
    #                                                                 Mobile Number: %s</br></br>
    #                                                                 Requestor : %s.<br/>
    #                                                                 <strong>Thank You</strong>
    #                                                             </body>
    #                                                         <html>""" % (
    #                     reciever.name, record.id, record.name, record.order_placed_date, record.partner_id.name,
    #                     record.partner_id.mobile, admin_user.name)
    #                 mail_message = MailThread.message_notify(body='<pre>%s</pre>' % message,
    #                                                          subject='New Orders has been placed!',
    #                                                          subtype='mail.mt_comment',
    #                                                          partner_ids=(reciever.partner_id).ids,
    #                                                          email_from=admin_user.login)
    #                 notif_create_values = [{
    #                     'mail_message_id': mail_message.id,
    #                     'res_partner_id': reciever.partner_id.id,
    #                     'notification_type': 'inbox',
    #                     'notification_status': 'sent',
    #                 }]
    #                 if notif_create_values:
    #                     self.env['mail.notification'].sudo().create(notif_create_values)