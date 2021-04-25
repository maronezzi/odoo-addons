# coding: utf-8
# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
from urllib import error
from bs4 import BeautifulSoup

try:
    from erpbrasil.base.fiscal import cnpj_cpf, ie
    from erpbrasil.base import misc
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")


class vacina(models.Model):
    _name = 'vacina.vacina'
    _description = "Controle de Vacina"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    data_vacina = fields.Date(required=True, default=lambda self: self._get_current_date())
    vacina_id = fields.Many2one(comodel_name="product.template", string="Vacina", )
    vacina_ext = fields.Char(string="Vacina Externa",  )

    cliente_id = fields.Many2one(comodel_name="res.partner", string="Paciente", required=True, )
    aniversario = fields.Char("Idade", related='cliente_id.age')

    enfermeira_id = fields.Many2one(comodel_name="hr.employee", string="Enfermeira", required=False, )
    enfermeira_ext = fields.Char(string="Enfermeira Ext.", required=False, )

    local_aplicacao = fields.Selection(
        [('sevacine', 'SeVacine'), ('ubs', 'UBS (Un. Básica de Saúde)'), ('particular', 'Particular')],
        string='Onde Foi Aplicada')

    final_lot_id = fields.Many2one(
        'stock.production.lot', 'Lote', domain="[('product_id', '=', vacina_id)]", )
    # validade = fields.Date(string='Validade', related='final_lot_id.life_date')

    lote_ext = fields.Char(string="Lote Externo", )

    # dose_aplicada = fields.Char(string="Dose Aplicada", required=False, )
    dose_aplicada = fields.Selection(
        [('primeira', '1º Dose'), ('segunda', '2º Dose'), ('terceira', '3º Dose'),
         ('unica', 'Dose Única'), ('reforço', 'Reforço'), ('anual', 'Anual')],
        string='Dose Aplicada')
    # observacao = fields.Text(string="Observaçes", required=False, )

    @api.model
    def _get_current_date(self):
        """ :return current date """
        return fields.Date.today()


class CicloFrio(models.Model):
    _name = 'ciclo.frio'
    _description = 'Modulo para Registro do Ciclo Frio'
    _inherit = ['mail.thread']

    data = fields.Datetime(string="Hora do Registro", required=True,)
    atual = fields.Float(string="Temperatura Atual", required=True, track_visibility='on_change')
    minima = fields.Float(string="Temperatura Mínima", required=True, track_visibility='on_change')
    maxima = fields.Float(string="Temperatura Máxima", required=True, track_visibility='on_change')
    current_user = fields.Many2one('res.users', 'Usuário', default=lambda self: self.env.user, readonly=True)
    temperatura = fields.Integer(string="Temperatura Belém", required=False)
    humidade = fields.Integer(string="Umidade Belém", required=False)
    condicao_atual = fields.Char(string="Condição do tempo", required=False)
    observacao = fields.Text(string="Observações", required=False, )

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

            hora_atual = datetime.now()
            self.data = hora_atual


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
    age = fields.Char(string="Idade" )
    identificacao = fields.Char(string="CPF", required=False, )
    carteira_vacina = fields.Binary(string="Cart. de Vacinação", )

    nfse = fields.Many2one(comodel_name="res.partner", string="NFSe", required=False, )
    mae = fields.Many2one(comodel_name="res.partner", string="Nome da Mãe", required=False, )
    pai = fields.Many2one(comodel_name="res.partner", string="Nome do Pai", required=False, )


    @api.onchange('identificacao')  # if these fields are changed, call method
    def check_change(self):
        self.identificacao = cnpj_cpf.formata(str(self.identificacao))

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
    pmc = fields.Monetary(string="Preço Máx. Cons.", required=False, track_visibility='on_change')

    @api.multi
    @api.onchange('list_price', 'pmc')
    def onchange_calculer(self):
        for s in self:
            s.gesto_vacinal = self.list_price - self.pmc

