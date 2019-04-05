# -*- coding: utf-8 -*-
from odoo import http

# class Concorrentes(http.Controller):
#     @http.route('/concorrentes/concorrentes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/concorrentes/concorrentes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('concorrentes.listing', {
#             'root': '/concorrentes/concorrentes',
#             'objects': http.request.env['concorrentes.concorrentes'].search([]),
#         })

#     @http.route('/concorrentes/concorrentes/objects/<model("concorrentes.concorrentes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('concorrentes.object', {
#             'object': obj
#         })