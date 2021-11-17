# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'
    _description = 'Account report with payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        for invoice in self.env['account.move'].browse(docids):
            invoice.print_count += 1
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }
