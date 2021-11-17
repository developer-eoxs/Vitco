from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, ValidationError
import io as io
from io import BytesIO
import base64
import xlsxwriter


class OdxSaleStatusReport(models.TransientModel):
    _name = 'odx.sale.status.report'
    _description = 'Sale Status Report'

    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: self._context.get('date_from', datetime.today().replace(day=1)))
    date_to = fields.Date(string='To Date', required=True)

    @api.onchange('date_from')
    def last_day_of_month(self):
        if self.date_from:
            any_day = datetime.strptime(str(self.date_from), '%Y-%m-%d')
            next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
            to_date = next_month - timedelta(days=next_month.day)
            to_date = to_date.strftime('%Y-%m-%d')
            self.date_to = to_date

    def action_sale_status_report(self):
        return self.env.ref('odx_product_custom_steel.sale_status_report_xlsx').report_action(self)
