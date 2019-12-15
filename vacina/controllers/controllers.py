# -*- coding: utf-8 -*-
from odoo import http

# class Vacina(http.Controller):
#     @http.route('/vacina/vacina/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vacina/vacina/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vacina.listing', {
#             'root': '/vacina/vacina',
#             'objects': http.request.env['vacina.vacina'].search([]),
#         })

#     @http.route('/vacina/vacina/objects/<model("vacina.vacina"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vacina.object', {
#             'object': obj
#         })