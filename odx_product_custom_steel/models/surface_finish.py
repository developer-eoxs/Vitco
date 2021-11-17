from odoo import models, fields, api


class SurfaceFinish(models.Model):
    _name = 'surface.finish'

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
