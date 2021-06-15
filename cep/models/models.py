# -*- coding: utf-8 -*-

from odoo import models, fields, api
import urllib.request, json

class cep(models.Model):
    _name = 'cep.cep'
    _inherit = "res.partner"

    # name = fields.Char()
    # value = fields.Integer()
    # value2 = fields.Float(compute="_value_pc", store=True)
    # description = fields.Text()

    @api.multi
    @api.onchange('zip', 'city')  # if these fields are changed, call method
    def check_change(self):
        with urllib.request.urlopen("https://viacep.com.br/ws/66083340/json/") as url:
            data = json.loads(url.read().decode())
            print(data)

