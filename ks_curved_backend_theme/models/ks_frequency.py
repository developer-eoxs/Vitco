from odoo import models, fields


class KsFrequnencyCounter(models.Model):
    _name = "ks.frequency.counter"
    _description = "Apps Frequency"

    ks_frequency = fields.Integer(string="Frequency", default=0)
    ks_user_id = fields.Many2one(string="User", comodel_name="res.users", required=True, help="Connected User")
    ks_menu_id = fields.Many2one(string="Menu", comodel_name="ir.ui.menu",required=True,  help="Menu List")
#

