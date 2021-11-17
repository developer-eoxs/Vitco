import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/send_back'], type='http', auth="public", website=True)
    def portal_quote_send_back(self, order_id, access_token=None, name=None, signature=None):
        print('accept and sign')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
            order_sudo.write({
                'send_back_status': 'option_received',
            })
            # 'require_signature': True,
            print(order_sudo,"sudo")
            query_string = "Your Order is Under Process"
            # order_sudo.get_portal_url()
            return request.redirect(order_sudo.get_portal_url(anchor='details'))
            # return request.redirect(order_sudo.get_portal_url(query_string=query_string))
            # return request.redirect('/my')
        except (AccessError, MissingError):
            return request.redirect('/my')
