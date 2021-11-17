from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def daily_transporter_email(self):
        print ("dddddddddddddddddd")
        print ("dddddddddddddddddd")
        print ("dddddddddddddddddd")
        print ("dddddddddddddddddd",self)
        for line in self:
            template_id = self.env.ref('odx_km_freight_management.mail_template_transport_detail_mail').id
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            if template.lang:
                lang = template._render_template(template.lang, 'res.partner', line.ids[0])
            ctx = {
                'default_model': 'res.partner',
                'default_res_id': line.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'model_description': 'test',
            }
        return {
            'name': _('Send Transporter Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }