# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadLost(models.TransientModel):
    _name = 'vrm.lead.lost'
    _description = 'Get Lost Reason'

    lost_reason_id = fields.Many2one('vrm.lost.reason', 'Lost Reason')

    def action_lost_reason_apply(self):
        leads = self.env['vrm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id)
