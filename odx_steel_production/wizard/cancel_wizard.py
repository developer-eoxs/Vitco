from odoo import models, fields, api, _


class ProductionCancelWizard(models.TransientModel):
    _name = 'production.cancel.wizard'

    production_id = fields.Many2one('steel.production', string="Production Ref")

    def cancel_production(self):
        if self.production_id.state != 'done' and self.production_id.pro_multi_lot_line_ids:
            self.production_id.write({
                'state': 'cancel'
            })
            for rec in self.production_id.pro_multi_lot_line_ids:
                rec.lot_id.stock_status = 'available'
                rec.lot_status = 'available'
