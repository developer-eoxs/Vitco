# -*- coding: utf-8 -*-
# from odoo import http


# class HideMenus(http.Controller):
#     @http.route('/hide_menus/hide_menus/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_menus/hide_menus/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_menus.listing', {
#             'root': '/hide_menus/hide_menus',
#             'objects': http.request.env['hide_menus.hide_menus'].search([]),
#         })

#     @http.route('/hide_menus/hide_menus/objects/<model("hide_menus.hide_menus"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_menus.object', {
#             'object': obj
#         })
