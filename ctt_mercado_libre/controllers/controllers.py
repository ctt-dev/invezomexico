# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi

import logging
_logger = logging.getLogger(__name__)

class MercadoLibreLogin(http.Controller):

    @http.route(['/meli_code'], type='http', auth="user", methods=['GET'], website=True)
    def index(self, **codes ):
    
        codes.setdefault('code','none')
        codes.setdefault('error','none')
        
        if codes['code'] != 'none':
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_code', codes['code'])

            params = request.env['ir.config_parameter'].sudo()
            client_id = params.get_param('ctt_mercado_libre.mercado_libre_app_id')
            client_secret = params.get_param('ctt_mercado_libre.mercado_libre_client_secret')
            redirect_uri = params.get_param('ctt_mercado_libre.mercado_libre_redirect_url')

            api_conecctor = MeliApi({
                'client_id': client_id,
                'client_secret': client_secret,
                'tg_code': codes['code'],
                'redirect_uri': redirect_uri
            })

            tokens = api_conecctor.authorize()

            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token', tokens['access_token'])
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_refresh_token', tokens['refresh_token'])
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_is_connect', True)
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_valido', True)

        server_action = request.env.ref("ctt_mercado_libre.redirect_settings_action")
        return request.redirect(
            '/web#action=%s&model=res.config.settings' % (server_action.id))