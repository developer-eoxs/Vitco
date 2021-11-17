# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _is_vrm_lead(self, defaults, ctx=None):
        """
            This method checks if the concerned model is a CRM lead.
            The information is not always in the defaults values,
            this is why it is necessary to check the context too.
        """
        res_model = defaults.get('res_model', False) or ctx and ctx.get('default_res_model')
        res_model_id = defaults.get('res_model_id', False) or ctx and ctx.get('default_res_model_id')

        return res_model and res_model == 'vrm.lead' or res_model_id and self.env['ir.model'].sudo().browse(res_model_id).model == 'vrm.lead'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_vrm_lead_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('odx_vrm.model_vrm_lead').id,
                default_res_id=self.env.context['default_vrm_lead_id']
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to opportunity id (aka creating meeting from lead chatter)
        ctx = self.env.context
        if 'vrm_lead_id' not in defaults:
            if self._is_vrm_lead(defaults, ctx):
                defaults['vrm_lead_id'] = defaults.get('res_id', False) or ctx.get('default_res_id', False)

        return defaults

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get('active_model') == 'vrm.lead':
            vrm_lead_id = self.env.context.get('active_id')
            for event in self:
                if event.vrm_lead_id.id == vrm_lead_id:
                    event.is_highlighted = True

    vrm_lead_id = fields.Many2one('vrm.lead', 'VRM Lead', domain="[('type', '=', 'opportunity')]")

    @api.model
    def create(self, vals):
        events = super(CalendarEvent, self).create(vals)

        if events.vrm_lead_id and not events.activity_ids:
            events.vrm_lead_id.log_meeting(events.name, events.start, events.duration)
        return events
