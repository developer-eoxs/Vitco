from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # heat_number = fields.Char(string='Heat Number')
    # lift_number = fields.Char(string='Lift Number')
    # part_number = fields.Char(string='Part Number')
    # tag_number = fields.Char(string='Tag Number')
    vendor_serial_number = fields.Char(string='Vendor Serial Number')
