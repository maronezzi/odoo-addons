# -*- coding: utf-8 -*-
from odoo import http

# class Cep(http.Controller):
#     @http.route('/cep/cep/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cep/cep/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cep.listing', {
#             'root': '/cep/cep',
#             'objects': http.request.env['cep.cep'].search([]),
#         })

#     @http.route('/cep/cep/objects/<model("cep.cep"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cep.object', {
#             'object': obj
#         })