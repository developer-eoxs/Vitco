from odoo import models, fields, api, _


class JobOrderCancelWizard(models.TransientModel):
    _name = 'job.order.cancel.wizard'

    job_order_id = fields.Many2one('job.order', string="Job Ref")

    def cancel_job_order(self):
        if self.job_order_id.state != 'done' and self.job_order_id.multi_lot_line_ids:
            self.job_order_id.write({
                'state': 'cancel'
            })
            for rec in self.job_order_id.multi_lot_line_ids:
                rec.lot_id.stock_status = 'available'
                rec.lot_status = 'available'
