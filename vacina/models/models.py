# coding: utf-8
# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from urllib.request import urlopen
import urllib.request, json
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

    data_vacina = fields.Datetime(required=True, default=lambda self: self._get_current_date())
    vacina_id = fields.Many2one(comodel_name="product.template", string="Vacina", )
    vacina_ext = fields.Char(string="Vacina Externa",  )

    cliente_id = fields.Many2one(comodel_name="res.partner", string="Paciente", required=True, )
    aniversario = fields.Char("Idade", related='cliente_id.age')
    nascimento = fields.Date("nascimento", related='cliente_id.birthdate')

    enfermeira_id = fields.Many2one(comodel_name="hr.employee", string="Enfermeira", required=False)
    enfermeira_ext = fields.Char(string="Enfermeira Ext.", required=False, )

    idadevacina = fields.Char(string="Idade dia Vacina")

    local_aplicacao = fields.Selection(
        [('sevacine', 'SeVacine'), ('ubs', 'UBS (Un. Básica de Saúde)'), ('particular', 'Particular')],
        string='Onde Foi Aplicada')

    final_lot_id = fields.Many2one(
        'stock.production.lot', 'Lote', domain="[('product_id', '=', vacina_id)]", )
    # validade = fields.Date(string='Validade', related='final_lot_id.life_date')

    lote_ext = fields.Char(string="Lote Externo", required=True, )

    # dose_aplicada = fields.Char(string="Dose Aplicada", required=False, )
    dose_aplicada = fields.Selection(
        [('primeira', '1º Dose'), ('segunda', '2º Dose'), ('terceira', '3º Dose'),
         ('unica', 'Dose Única'), ('reforço', 'Reforço'), ('anual', 'Anual')],
        string='Dose Aplicada')

    aplicacao = fields.Selection(
        [('pernadireita', 'Perna Direita'), ('pernaesq', 'Perna Esquerda'),
         ('bracodireito', 'Braço Direito'), ('bracoesquerdo', 'Braço Esquerdo'),
         ],
        string='Local da Aplicação')

    @api.model
    def _get_current_date(self):
        """ :return current date """
        return fields.Datetime.now()

    @api.multi
    @api.onchange('aplicacao')
    def idadeaplica(self):
        if not self.nascimento:
            return

        d1 = datetime.strptime(str(self.nascimento), "%Y-%m-%d").date()
        d2 = datetime.strptime(str(self.data_vacina.date()), "%Y-%m-%d").date()
        self.idadevacina = str(relativedelta(d2, d1).years) + " Anos, " + str(
            relativedelta(d2, d1).months) + " Meses e " + str(relativedelta(d2, d1).days) + " dias"


class CicloFrio(models.Model):
    _name = 'ciclo.frio'
    _description = 'Modulo para Registro do Ciclo Frio'
    _inherit = ['mail.thread']

    data = fields.Datetime(string="Hora do Registro", required=True, default=lambda self: self._get_current_date())
    atual = fields.Float(string="Temperatura Atual", required=True,)
    minima = fields.Float(string="Temperatura Mínima", required=True, )
    maxima = fields.Float(string="Temperatura Máxima", required=True, )
    current_user = fields.Many2one('res.users', 'Usuário', default=lambda self: self.env.user, readonly=True)
    temperatura = fields.Char(string="Temperatura Belém")
    humidade = fields.Char(string="Umidade Belém")
    condicao_atual = fields.Char(string="Condição do tempo", )
    observacao = fields.Text(string="Observações", )

    refrigerador = fields.Selection(
        [('refrigerador_1', 'Refrigerador 1'), ('refrigerador_2', 'Refrigerador 2'),
         ],
        string='Refrigerador', required=True)
    @api.multi
    @api.onchange('atual')
    def temp(self):
        try:
            html = urlopen("http://servicos.cptec.inpe.br/XML/estacao/SBBE/condicoesAtuais.xml").read()
            soup = BeautifulSoup(html, "lxml")

            # print("Atualizacao: %s" % soup.atualizacao.get_text())
            temp_inmet = soup.temperatura.get_text()
            self.temperatura = temp_inmet + "ºC"

            umid_inmet = soup.umidade.get_text()
            self.humidade = umid_inmet + "%"

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
    @api.model
    def _get_current_date(self):
        """ :return current date """
        return fields.Datetime.now()

class BirthDateAge(models.Model):
    _inherit = "res.partner"

    birthdate = fields.Date(string="Data do Nascimento")
    age = fields.Char(string="Idade" )
    identificacao = fields.Char(string="CPF", required=False, )
    carteira_vacina = fields.Binary(string="Cart. de Vacinação", )

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



class cep(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.onchange('zip', 'city')  # if these fields are changed, call method
    def on_change_state(self):

        if not self.zip:
            return

        zip_str = self.zip.replace('-', '')
        print(zip_str)

        if len(zip_str) == 8:

            with urllib.request.urlopen("https://viacep.com.br/ws/"+zip_str+"/json/") as url:
                data = json.loads(url.read().decode())

                self.city = data['localidade']
                self.street = data['logradouro']
                self.street2 = data['bairro']

                # Search Brazil id
                country_ids = self.env['res.country'].search(
                    [('code', '=', 'BR')])

                # Search state with state_code and country id
                state_ids = self.env['res.country.state'].search([
                    ('code', '=', str(data['uf'])),
                    ('country_id.id', 'in', country_ids.ids)])

                self.state_id = state_ids.ids[0]
                self.country_id = country_ids.ids[0]


class cep(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.onchange('street', 'street2', 'city')  # if these fields are changed, call method
    def uf_country(self):
        if not self.zip:
            # Search Brazil id
            country_ids = self.env['res.country'].search(
                [('code', '=', 'BR')])

            # Search state with state_code and country id
            state_ids = self.env['res.country.state'].search([
                ('code', '=', "PA"),
                ('country_id.id', 'in', country_ids.ids)])

            self.state_id = state_ids.ids[0]
            self.country_id = country_ids.ids[0]
            self.city = "Belém"