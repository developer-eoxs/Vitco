from odoo import models, fields, api


class Components(models.Model):
    _name = 'product.components'

    name = fields.Char(string="Components",store=True)
    value = fields.Float(string="Values")
    component_id = fields.Many2one('product.template', string='Components')
    stock_component_id = fields.Many2one('stock.production.lot', string='Components')
