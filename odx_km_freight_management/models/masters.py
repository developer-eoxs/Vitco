# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class FrmVehicle(models.Model):
    _name = 'frm.vehicle'
    _description = 'FRM Vehicle'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    license_plate = fields.Char(string="Licence")
    model = fields.Char(string="Model")
    loading_type = fields.Selection([('side', 'Side'), ('back', 'Back')], string="Loading Type")
    seats = fields.Integer(string="Seats Number")
    doors = fields.Integer(string="Doors Number")
    color = fields.Char(string="Color")
    model_year = fields.Char(string="Model Year")

    @api.constrains('code')
    def _check_duplicate_name(self):
        codes = self.search([])
        for c in codes:
            if self.code.lower() == c.code.lower() and self.id != c.id:
                raise ValidationError("Error: Vehicle Code must be unique")


class FrmLocation(models.Model):
    _name = 'frm.location'
    _description = 'FRM Location'

    name = fields.Char(string="Name of Wh")
    code = fields.Char(string="Code",default=lambda self: self.env['ir.sequence'].next_by_code('frm.location') or _('New'))
    country_id = fields.Many2one('res.country', string="Country")
    adress = fields.Char(string="Adress")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.name.lower() == c.name.lower() and self.id != c.id:
                raise ValidationError("Error: Location must be unique")


class FrmModeofOperation(models.Model):
    _name = 'frm.mode.operation'
    _description = 'FRM Mode of Operations'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.name.lower() == c.name.lower() and self.id != c.id:
                raise ValidationError("Error: Vehicle Code must be unique")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transporter = fields.Boolean(string="Transporter")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    freight = fields.Boolean(string="Is a Freight")
