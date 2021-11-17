from odoo import models, fields, api


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # message_main_attachment_id = fields.Many2one(string="Main Attachment", comodel_name='ir.attachment', index=True,
    #                                              copy=False)