from odoo import models, fields, exceptions, api


class LotSkid(models.Model):
    _name = 'lot.skid'

    tag = fields.Char(string="Tag", readonly=True, required=True, copy=False, default='New')
    name = fields.Char(string="Name")
    lot_ids = fields.Many2many('stock.production.lot', string="Lot", )
    # skid_lot_ids = fields.Many2many('steel.production.line', string="Lots", )
    # domain=[('production_ref_id', '=', "production_skid_id")]
    weight = fields.Float(string="Weight", compute="_total_weight", store=True)
    production_skid_id = fields.Many2one('steel.production', "Production Ref")

    @api.model
    def create(self, vals):
        if vals.get('tag', 'New') == 'New':
            vals['tag'] = self.env['ir.sequence'].next_by_code(
                'lot.skid') or 'New'
        result = super(LotSkid, self).create(vals)
        print(result)
        return result

    @api.depends('lot_ids')
    # @api.depends('skid_lot_ids')
    def _total_weight(self):
        for rec in self:
            total_weight = 0
            if rec.lot_ids:
                for lots in rec.lot_ids:
                    total_weight += lots.product_qty
            rec.weight = total_weight
