# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date




class concorrentes(models.Model):
    _name = 'concorrentes.concorrentes'
    _description = "Controle de Preços Concorrencia"
    _inherit = ['mail.thread']

    concorrentes_id = fields.Many2one(comodel_name="res.partner", string="Concorrentes", required=True, )
    vacina_id = fields.Many2one(comodel_name="product.template", string="Vacina", required=True, )

    data = fields.Date(string="Data da Cotaçao:", required=True, default=date.today(), track_visibility='on_change')
    preco_apurado = fields.Float(string="Preço Apurado:", required=True, track_visibility='on_change')
    preco_desconto = fields.Float(string="Preço c/ Desconto:", required=False, track_visibility='on_change')

