# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.parse import urlencode
from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
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
    mercado_libre_token_request_time = fields.Datetime(string="Fecha de obtención del token", config_parameter='ctt_mercado_libre.mercado_libre_token_request_time')
    mercado_libre_token_expires = fields.Datetime(string="Expiracion del token", config_parameter='ctt_mercado_libre.mercado_libre_token_expires')
    mercado_libre_is_connect = fields.Boolean(string="Conectado", default=False,config_parameter="ctt_mercado_libre.mercado_libre_is_connect")
    mercado_libre_token_valid = fields.Boolean(string="Token valido", config_parameter="ctt_mercado_libre.mercado_libre_token_valido")
    mercado_libre_user_id = fields.Char(string="Vendedor ID", config_parameter='ctt_mercado_libre.mercado_libre_user_id')


    def _refresh_ml_token(self):
        params = self.env['ir.config_parameter'].sudo()

        api_conector = MeliApi({
                'client_id': params.get_param('ctt_mercado_libre.mercado_libre_app_id'),
                'client_secret': params.get_param('ctt_mercado_libre.mercado_libre_client_secret'),
                'refresh_token': params.get_param('ctt_mercado_libre.mercado_libre_refresh_token'),
        })

        response = api_conector.refresh()

        init_time = datetime.now()
        request_time = datetime(init_time.year,init_time.month,init_time.day,init_time.hour,init_time.minute,init_time.second)
        expired_time = request_time + timedelta(seconds=response['expires_in'])

        self.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token', response['access_token'])
        self.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_refresh_token', response['refresh_token'])
        self.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_request_time', request_time)
        self.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_expires', expired_time)

        cron = self.env['ir.cron'].create({
            'name': "***Automated refresh ML Token",
            'model_id': request.env['ir.model.data']._xmlid_to_res_id('base.model_res_config_settings'),
            'interval_number': 1,
            'interval_type': 'hours',
            'active': True,
            'nextcall': expired_time,
            'numbercall': 1,
            'priority': 1,
            'doall': True,
            'code': """
                    env['res.config.settings']._refresh_ml_token()
                    """})

    def verify_ml_token(self):
        for rec in self:
            if datetime.now() >= rec.mercado_libre_token_request_time and datetime.now() <= rec.mercado_libre_token_expires:
                rec.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_valido', True)
            else:
                rec.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_valido', False)
    
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