# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    odometer = fields.Float(string='Last Odometer')
    odometer_unit = fields.Selection([
        ('km', 'Kilometers'),
        ('mi', 'Miles'),
    ], string='Odometer Unit', default='km', required=True)

    vin = fields.Char(string='VIN')
    damage = fields.Char(string='Damage')
    inspection = fields.Char(string='Inspection')
    closing_date = fields.Datetime(string='Closing Date')
    location_id = fields.Many2one('stock.location', string='Location')
    year = fields.Integer(string='Year')
    product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value',string='Model',
                                             related='product_id.product_template_attribute_value_ids')
    transmission = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ], string='Transmission')
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('lpg', 'LPG'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ], string='Fuel Type')
    emissions = fields.Float(string='CO2 Emissions')
    horsepower = fields.Integer(string='HorsePower')
    horsepower_taxation = fields.Float(string='Horsepower Taxation')
    power = fields.Integer(string='Power')
    seat_no = fields.Integer(string='Seat Number')
    door_no = fields.Integer(string='Door Number')
    chassis_no = fields.Char(string='Chassis Number')


