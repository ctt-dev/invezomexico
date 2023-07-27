# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.parse import urlencode
import logging
_logger = logging.getLogger(__name__)

class CTTMELIResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
   
    mercado_libre_app_id = fields.Char(string="App ID", config_parameter='ctt_mercado_libre.mercado_libre_app_id')
    mercado_libre_client_secret = fields.Char(string="Client secret", config_parameter='ctt_mercado_libre.mercado_libre_client_secret')
    mercado_libre_redirect_url = fields.Char(string="Redirect URL", config_parameter="ctt_mercado_libre.mercado_libre_redirect_url")
    mercado_libre_code = fields.Char(string="Code", config_parameter="ctt_mercado_libre.mercado_libre_code")
    mercado_libre_token = fields.Char(string="Token", config_parameter="ctt_mercado_libre.mercado_libre_token")
    mercado_libre_refresh_token = fields.Char(string="Refresh token", config_parameter="ctt_mercado_libre.mercado_libre_refresh_token")
    mercado_libre_is_connect = fields.Boolean(string="Conectado", default=False,config_parameter="ctt_mercado_libre.mercado_libre_is_connect")
    mercado_libre_token_valid = fields.Boolean(string="Token valido", config_parameter="ctt_mercado_libre.mercado_libre_token_valido")

    def _ml_redirect_settings(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("ctt_mercado_libre.mercado_libre_settings_menu_action")
        return action

    def auth_url(self):
        url = ""
        params = { 'client_id': self.mercado_libre_app_id, 'response_type':'code', 'redirect_uri':self.mercado_libre_redirect_url}
        url = "https://auth.mercadolibre.com.mx/authorization"  + '?' + urlencode(params)
        return url

    def mercado_libre_get_token(self):
        self.ensure_one()
        url_login_meli = str(self.auth_url())
        return {
            "type": "ir.actions.act_url",
            "url": url_login_meli,
            "target": "self",
        }