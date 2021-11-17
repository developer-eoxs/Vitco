from odoo import models, fields, api
from datetime import date

from odoo import SUPERUSER_ID


class AccountMove(models.Model):
    _inherit = 'account.move'

    def invoice_due_date_reminder(self):
        date_today = fields.Date.today()
        due_invoices = self.env['account.move'].search(
            [('invoice_date_due', '=', date_today), ('state', '=', 'posted'), ('amount_residual', '>', 0)])
        group = self.env.ref('odx_report_customisation.group_due_reminder_access')

        recipients = []
        body = ""
        for recipient in group.users:
            recipients.append(recipient)
        print(recipients)

        admin_user = self.env['res.users'].browse(SUPERUSER_ID)
        MailThread = self.env['mail.thread']
        recievers = []
        mail_vals = {}
        notification_ids = []
        header_label_list = ["S.No", "Inv No.", "Customer/Vendor", "Due Date", "Amount"]
        serial = 1
        message = ""

        if due_invoices:
            for reciever in recipients:
                email_from = admin_user.login
                subject = 'Invoice Due Date Notification!'
                message += """
                    <table class="table table-bordered">
                     <tr style="font-size:14px; border: 1px solid black">
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    <th style="text-align:center; border: 1px solid black">%s</th>
                    <th style="text-align:center; border: 1px solid black">%s</th>
                     <th style="text-align:center; border: 1px solid black">%s</th>
                     <th style="text-align:center; border: 1px solid black">%s</th>
                    </tr>
                  """ % (header_label_list[0], header_label_list[1], header_label_list[2],
                         header_label_list[3], header_label_list[4])

                for record in due_invoices:
                    message += """
                        <tr style="font-size:14px; border: 1px solid black">
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                            <td style="text-align:center; border: 1px solid black">%s</td>
                        </tr>
                        """ % (
                        serial, record.name, record.partner_id.name, record.invoice_date_due,
                        record.amount_residual)
                    serial += 1
                message += """</html>"""
                print("x1")

                mail_message = MailThread.message_notify(body='<pre>%s</pre>' % message,
                                                         subject='Invoice Due Date Notification!',
                                                         subtype='mail.mt_comment',
                                                         partner_ids=(reciever.partner_id).ids,
                                                         email_from=admin_user.login)
                notif_create_values = [{
                    'mail_message_id': mail_message.id,
                    'res_partner_id': reciever.partner_id.id,
                    'notification_type': 'inbox',
                    'notification_status': 'sent',
                }]
                if notif_create_values:
                    print("x")
                    self.env['mail.notification'].sudo().create(notif_create_values)
#
# header_label_list = ["S.No:", "Name", "Qty On Hand ", "Minimum Quantity"]
# serial = 1
# date_today = fields.Date.today()
# due_invoices = self.env['account.move'].search([('invoice_date_due', '=', date_today), ('state', '=', 'posted')])
# group = self.env.ref('account.group_account_manager')
#
# recipients = []
# body = ""
# for recipient in group.users:
#     recipients.append((4, recipient.partner_id.id))
# # Notification message body
# for record in self:
#     for rec in due_invoices:
#         body += """
#
#         <h2>%s<h2>
#         <table class="table table-bordered">
#             <tr style="font-size:14px; border: 1px solid black">
#                 <th style="text-align:center; border: 1px solid black">%s</th>
#                 <th style="text-align:center; border: 1px solid black">%s</th>
#                 <th style="text-align:center; border: 1px solid black">%s</th>
#                 <th style="text-align:center; border: 1px solid black">%s</th>
#                 </tr>
#              """ % (rec.name, header_label_list[0], header_label_list[1], header_label_list[2],
#                     header_label_list[3])
#         # for product_id in filtered_product_ids:
#         body += """
#             <tr style="font-size:14px; border: 1px solid black">
#                 <td style="text-align:center; border: 1px solid black">%s</td>
#                 <td style="text-align:center; border: 1px solid black">%s</td>
#                 <td style="text-align:center; border: 1px solid black">%s</td>
#                 <td style="text-align:center; border: 1px solid black">%s</td>
#             </tr>
#             """ % (serial, rec.name, rec.invoice_date_due, rec.partner_id.name)
#         serial += 1
#         body += """</table>"""
#         serial = 1
#
#     post_vars = {
#         'body': body,
#         'partner_ids': self.env.user.partner_id,
#         'subject': "Low stock notification",
#     }
#     print(post_vars,"pposttt")
#
#     partner_id = self.env.user.partner_id
#     thread_pool = self.env['mail.thread']
#     message_mail = self.env['mail.message'].create(post_vars)
#     thread_pool.message_post(
#         type="notification",
#         # partner_ids= ,
#         subtype="mt_comment",
#         **post_vars)
