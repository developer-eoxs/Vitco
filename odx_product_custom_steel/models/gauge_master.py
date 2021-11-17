from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError


class SteelGauge(models.Model):
    _name = 'steel.gauge'

    name = fields.Char(string="Name")
    gauge_no = fields.Integer(string="Gauge No.")
    gauge_inch = fields.Float(string="Gauge(inch)", digits=[6, 4])
    gauge_mm = fields.Float(string="Gauge(mm)", digits=[6, 2])


class ThicknessRange(models.Model):
    _name = 'thickness.range'

    name = fields.Char(string="Name")
    thk_ll = fields.Float(string="Thk Lower Limit", digits=[6, 4])
    thk_ul = fields.Float(string="Thk Upper Limit)", digits=[6, 4])
