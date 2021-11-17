# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, exceptions, api, _
from datetime import datetime


class ProductionMachine(models.Model):
    _name = 'production.machine'

    machine_code = fields.Char(string="Machine Code")
    name = fields.Char(string="Machine Name")
    machine_scheduler_ids = fields.One2many('machine.scheduler', 'machine_id', string="Machine Scheduler")


class MachineScheduler(models.Model):
    _name = 'machine.scheduler'
    _order = 'id, sequence asc'

    machine_id = fields.Many2one('production.machine', string="Machine Id")
    sequence = fields.Integer(string='Sequence', default=10)
    work_order_id = fields.Many2one('production.instructions', string="Work order")
    pr_run_id = fields.Many2one('instructions.run.line', string="Production Run",
                                domain="[('prod_inst_ref_id', '=', work_order_id) or [] ] ")
    next_pr_run_id = fields.Many2one('instructions.run.line', string="Next Production Run")
    due_date = fields.Datetime(string="Due Date")
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    state = fields.Selection([
        ('pending', 'Waiting for another WO'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        default='pending')
    working_state = fields.Selection([
        ('normal', 'Normal'),
        ('blocked', 'Blocked'),
        ('done', 'In Progress')], 'Workcenter Status', default='normal')
    # is_user_working = fields.Boolean(
    #     'Is the Current User Working',
    #     help="Technical field indicating whether the current user is working. ")
    is_user_working = fields.Boolean(
        'Is the Current User Working', compute='_compute_working_users',
        help="Technical field indicating whether the current user is working. ")
    working_user_ids = fields.One2many('res.users', string='Working user on this work order.', compute='_compute_working_users')
    last_working_user_id = fields.One2many('res.users', string='Last user that worked on this work order.', compute='_compute_working_users')
    time_ids = fields.One2many(
        'production.run.block', 'machine_scheduler_id')

    def record_production(self):
        if self.pr_run_id.finish_picking_id:
            try:
                self.pr_run_id.finish_picking_id.action_confirm()
                self.pr_run_id.finish_picking_id.with_context({'baby_lot': True}).button_validate()
            except:
                pass
        self.write({'state': 'done', 'end_time': datetime.now()})
        if self.next_pr_run_id:
            next_pr_run_id = self.search([('pr_run_id', '=', self.next_pr_run_id.id)], limit=1)
            if next_pr_run_id.state == 'pending':
                next_pr_run_id.state = 'ready'
        workorder_machine_scheduler_ids = self.search([
            ('work_order_id', '=', self.work_order_id.id),
            ('state', '!=', 'done')])
        if not workorder_machine_scheduler_ids:
            self.work_order_id.state = 'produced'
        return True

    def _compute_working_users(self):
        for order in self:
            order.working_user_ids = [(4, order.id) for order in order.time_ids.filtered(lambda time: not time.date_end).sorted('date_start').mapped('user_id')]
            if order.working_user_ids:
                order.last_working_user_id = order.working_user_ids[-1]
            elif order.time_ids:
                order.last_working_user_id = order.time_ids.filtered('date_end').sorted('date_end')[-1].user_id if order.time_ids.filtered('date_end') else order.time_ids[-1].user_id
            else:
                order.last_working_user_id = False
            if order.state in ['ready', 'pending'] or order.time_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end)):
                order.is_user_working = True
            else:
                order.is_user_working = False

    def end_previous(self, doall=False):
        timeline_obj = self.env['production.run.block']
        domain = [('machine_scheduler_id', 'in', self.ids), ('date_end', '=', False)]
        if not doall:
            domain.append(('user_id', '=', self.env.user.id))
        # not_productive_timelines = timeline_obj.browse()
        for timeline in timeline_obj.search(domain, limit=None if doall else 1):
            maxdate = fields.Datetime.from_string(timeline.date_start)
            enddate = datetime.now()
            timeline.write({'date_end': enddate})
            # if maxdate > enddate:
            #     timeline.write({'date_end': enddate})
            # else:
            #     timeline.write({'date_end': maxdate})
            #     not_productive_timelines += timeline.copy({'date_start': maxdate, 'date_end': enddate})
        # if not_productive_timelines:
        #     loss_id = self.env['production.run.block.type'].search([('loss_type', '=', 'performance')], limit=1)
        #     if not len(loss_id):
        #         loss_id = self.env['production.run.block.type'].create({
        #             'loss_type': 'performance',
        #             'name': 'Performance'
        #         })
        #     not_productive_timelines.write({'loss_id': loss_id.id})
        return True

    def end_all(self):
        return self.end_previous(doall=True)

    def button_pending(self):
        self.end_previous()
        return True

    def button_start(self):
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            return True

        check_previous_line = self.search([
            ('machine_id', '=', self.machine_id.id),
            ('work_order_id', '=', self.work_order_id.id),
            ('pr_run_id', '<', self.pr_run_id.id),
            ('state', '!=', 'done')
        ])
        if check_previous_line:
            production_name = "<br/>"
            production_name += "<br/>".join([i.pr_run_id.name for i in check_previous_line])
            context = dict(self.env.context)
            context.update({'message': production_name})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'confirm.next.pr.wizard',
                'target': 'new',
                'context': context,
            }
            # raise UserError(_("Please finish below Production Run first! \n %s") % (production_name))
        return self.generate_start_operation()

    def generate_start_operation(self):
        timeline = self.env['production.run.block']
        loss_id = self.env['production.run.block.type'].search([('loss_type', '=', 'productive')], limit=1)
        if not loss_id:
            loss_id = self.env['production.run.block.type'].create({
                'loss_type': 'productive',
                'name': 'Productive'
            })
        timeline.create({
            'work_order_id': self.work_order_id.id,
            'pr_run_id': self.pr_run_id.id,
            'description': _('Time Tracking: ')+self.env.user.name,
            'loss_id': loss_id[0].id,
            'date_start': datetime.now(),
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'machine_id': self.machine_id.id,
            'machine_scheduler_id': self.id,
        })
        if self.state == 'progress':
            return True
        start_date = datetime.now()
        vals = {
            'state': 'progress',
            'start_time': start_date,
        }
        return self.write(vals)

    def button_unblock(self):
        self.ensure_one()
        if self.working_state != 'blocked':
            raise exceptions.UserError(_("It has already been unblocked."))
        self.write({
            # 'is_user_working': True,
            'working_state': 'normal'})
        times = self.env['production.run.block'].search([('machine_scheduler_id', '=', self.id), ('date_end', '=', False)])
        print("==times==", times)
        times.write({'date_end': fields.Datetime.now()})
        return {'type': 'ir.actions.client', 'tag': 'reload'}
