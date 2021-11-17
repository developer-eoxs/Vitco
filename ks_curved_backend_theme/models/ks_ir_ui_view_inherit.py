from odoo import models, fields, _


class KsView(models.Model):
    _inherit = "ir.ui.view"

    ks_users = fields.One2many(inverse_name='ks_ir_ui_view', comodel_name="res.users", string='User')
    ks_users_ids = fields.Many2many(comodel_name="res.users", string='Users')
