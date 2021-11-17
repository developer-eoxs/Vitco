# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def res_user_menu_action(self):
        tree_view = self.env.ref('base.view_users_tree')
        form_view = self.env.ref('base.view_users_form')

        if not self.env.user.id == 2:
            user_ids = self.env['res.users'].search([('id', '=', 2)])
            domain = [('id', 'not in', user_ids.ids)]
            print(domain)
        else:
            domain = False
            print(domain)

        return {
            'name': _('Users'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'res.users',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'view_id': tree_view.id,
            'domain': domain

            # 'context': "{'delete':0}"
        }

    def write(self, values):
        for rec in self:
            if rec.id in [1,2]:
                print("x")
                if not self.env.user.id in [1,2]:
                    raise UserError(
                        _("You have no permission to edit this document.Please Contact Administrator"))

        res = super(ResUsers, self).write(values)
        return res
