# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductionRunBlockType(models.Model):
    _name = "production.run.block.type"
    _description = "Production Run Block Type"
    _order = "sequence, id"

    name = fields.Char('Blocking Reason', required=True)
    sequence = fields.Integer('Sequence', default=1)
    loss_type = fields.Selection([
            ('availability', 'Availability'),
            ('performance', 'Performance'),
            ('quality', 'Quality'),
            ('productive', 'Productive')], string='Category', default='availability', required=True)

class ProductionRunBlock(models.Model):
    _name = "production.run.block"
    _description = "Production Run Block"
    _order = "id desc"

    pr_run_id = fields.Many2one('instructions.run.line', string='Manufacturing Order')
    machine_id = fields.Many2one('production.machine', string="Machine Id")
    machine_scheduler_id = fields.Many2one('machine.scheduler', string="Machine Scheduler")
    company_id = fields.Many2one(
        'res.company', required=True, index=True,
        default=lambda self: self.env.company)
    work_order_id = fields.Many2one('production.instructions', 'Work Order', check_company=True)
    user_id = fields.Many2one(
        'res.users', "User",
        default=lambda self: self.env.uid)
    loss_id = fields.Many2one('production.run.block.type', "Block Reason",
        ondelete='restrict', required=True)
    description = fields.Text('Description')
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')
    duration = fields.Float('Duration', compute='_compute_duration', store=True)

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if blocktime.date_end:
                d1 = fields.Datetime.from_string(blocktime.date_start)
                d2 = fields.Datetime.from_string(blocktime.date_end)
                diff = d2 - d1
                blocktime.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                blocktime.duration = 0.0

    def button_block(self):
        self.machine_scheduler_id.write({
            'working_state': 'blocked'
        })
        self.machine_scheduler_id.end_all()


class ConfirmNextPRWizard(models.TransientModel):
    _name = 'confirm.next.pr.wizard'
    _description = 'Confirm Next PR Wizard'

    @api.model
    def default_get(self, fields_default):
        rec = super(ConfirmNextPRWizard, self).default_get(fields_default)
        machine_scheduler_id = self.env['machine.scheduler'].browse(self.env.context['active_ids'])
        rec['machine_scheduler_id'] = machine_scheduler_id.id
        rec['message'] = self.env.context['message']
        return rec

    message = fields.Html('Message')
    machine_scheduler_id = fields.Many2one('machine.scheduler', string="Scheduler Machine")

    def button_confirm(self):
        return self.machine_scheduler_id.generate_start_operation()
