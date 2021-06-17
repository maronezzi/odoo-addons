# -*- coding: utf-8 -*-

from odoo import models, fields, api
import urllib.request, json

class cep(models.Model):
    _name = 'cep.cep'
    _inherit = "res.partner"

    name = fields.Char()
    value = fields.Integer()
    description = fields.Text()

    @api.multi
    @api.onchange('zip', 'city')  # if these fields are changed, call method
    def on_change_state(self):
        print('gggg')
        with urllib.request.urlopen("https://viacep.com.br/ws/66083340/json/") as url:
            data = json.loads(url.read().decode())
            print(data)

