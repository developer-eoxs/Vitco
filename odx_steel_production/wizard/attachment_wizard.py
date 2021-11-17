from odoo import models, fields, api, _


class SaleAttachWizard(models.TransientModel):
    _name = 'production.sale.attach.wizard'

    production_id = fields.Many2one('steel.production', string="Production Ref")
    job_id = fields.Many2one('job.order', string="Job Ref")
