# coding: utf-8
# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
from urllib import error
from bs4 import BeautifulSoup


class vacina(models.Model):
    _name = 'vacina.vacina'
    _description = "Controle de Vacina"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    data_vacina = fields.Date(string="Data da Vacina", required=True, default=date.today())
    vacina_id = fields.Many2one(comodel_name="product.template", string="Vacina", )
    vacina_ext = fields.Char(string="Vacina Externa",  )


    cliente_id = fields.Many2one(comodel_name="res.partner", string="Paciente", required=True, )
    aniversario = fields.Char("Idade", related='cliente_id.age')


    enfermeira_id = fields.Many2one(comodel_name="hr.employee", string="Enfermeira", required=False, )
    enfermeira_ext = fields.Char(string="Enfermeira", required=False, )

    local_aplicacao = fields.Selection(
        [('sevacine', 'SeVacine'), ('ubs', 'UBS (Unidade Basica de Saude)'), ('particular', 'Particular')],
        string='Onde Foi Aplicada')
    final_lot_id = fields.Many2one(
        'stock.production.lot', 'Lote', domain="[('product_id', '=', vacina_id)]", )
    lote_ext = fields.Char(string="Lote Externo", )

    dose_aplicada = fields.Char(string="Dose Aplicada", required=False, )
    # observacao = fields.Text(string="Observaçes", required=False, )


class CicloFrio(models.Model):
    _name = 'ciclo.frio'
    _description = 'Modulo para Registro do Ciclo Frio'
    _inherit = ['mail.thread']

    data = fields.Datetime(string="Hora do Registro", required=True, default=datetime.now())
    atual = fields.Float(string="Temperatura Atual", required=True, track_visibility='on_change')
    minima = fields.Float(string="Temperatura Minima", required=True, track_visibility='on_change')
    maxima = fields.Float(string="Temperatura Maxima", required=True, track_visibility='on_change')
    current_user = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user, readonly=True)
    temperatura = fields.Integer(string="Temperatura Belem", required=False)
    humidade = fields.Integer(string="Umidade Belem", required=False)
    condicao_atual = fields.Char(string="Condicao do tempo", required=False)
    observacao = fields.Text(string="Observaçoes", required=False, )

    @api.multi
    @api.onchange('atual')
    def temp(self):
        try:
            html = urlopen("http://servicos.cptec.inpe.br/XML/estacao/SBBE/condicoesAtuais.xml").read()
            soup = BeautifulSoup(html, "lxml")

            # print("Atualizacao: %s" % soup.atualizacao.get_text())
            temp_inmet = soup.temperatura.get_text()
            self.temperatura = temp_inmet

            umid_inmet = soup.umidade.get_text()
            self.humidade = umid_inmet

            condicao_inmet = soup.tempo_desc.get_text()
            self.condicao_atual = condicao_inmet

        except error.URLError as e:
            if hasattr(e, 'code'):
                print(e.code)
            if hasattr(e, 'reason'):
                print(e.reason)
            self.temperatura = 0
            self.humidade = 0
            self.condicao_atual = "Sem acesso a Internet"

        except error.HTTPError as e:
            if hasattr(e, 'code'):
                print(e.code)
            if hasattr(e, 'reason'):
                print(e.reason)
            self.temperatura = 0
            self.humidade = 0
            self.condicao_atual = "Sem acesso a Internet"


class BirthDateAge(models.Model):
    _inherit = "res.partner"

    birthdate = fields.Date(string="Data do Nascimento")
    age = fields.Char(string="Idade")
    identificacao = fields.Char(string="Cart. de Identificaçao", required=False, )
    carteira_vacina = fields.Binary(string="Cart. de Vacinaçao", )

    mae = fields.Many2one(comodel_name="res.partner", string="Nome da Mae", required=False, )
    pai = fields.Many2one(comodel_name="res.partner", string="Nome do Pai", required=False, )

    @api.onchange('birthdate')
    def _onchange_birth_date(self):
        """Updates age field when birthdate is changed"""
        if self.birthdate:
            d1 = datetime.strptime(str(self.birthdate), "%Y-%m-%d").date()
            d2 = date.today()
            self.age = str(relativedelta(d2, d1).years) + " Anos, " + str(
                relativedelta(d2, d1).months) + " Meses e " + str(relativedelta(d2, d1).days) + " dias"

    @api.model
    def update_ages(self):
        """Updates age field for all partners once a day"""
        for rec in self.env['res.partner'].search([]):
            if rec.birthdate:
                d1 = datetime.strptime(str(rec.birthdate), "%Y-%m-%d").date()
                d2 = date.today()
                rec.age = str(relativedelta(d2, d1).years) + " Anos, " + str(
                    relativedelta(d2, d1).months) + " Meses e " + str(relativedelta(d2, d1).days) + " dias"


class GestoVacina(models.Model):
    _inherit = "product.template"

    gesto_vacinal = fields.Monetary(string="Gesto Vacinal", required=False, track_visibility='on_change')
    pmc = fields.Monetary(string="Preço Max. Cons.", required=False, track_visibility='on_change')

    @api.multi
    @api.onchange('list_price', 'pmc')
    def onchange_calculer(self):
        for s in self:
            s.gesto_vacinal = self.list_price - self.pmc
