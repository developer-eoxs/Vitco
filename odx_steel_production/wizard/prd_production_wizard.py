from odoo import models, fields, api, _


class ProductionConfirmWizard(models.TransientModel):
    _name = 'production.confirm.wizard'

    instruction_line_id = fields.Many2one('instructions.run.line', string="Instruction Line Ref")

