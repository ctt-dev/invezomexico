# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from odoo.addons.ctt_mercado_libre.utils.utils import MeliApi
import json

import logging
_logger = logging.getLogger(__name__)

class MercadoLibre(http.Controller):
    @http.route(['/meli_notify'], type='json', auth='public')
    def meli_notify(self,**kw):
        _logger.warning("NOTIFICACION MERCADO LIBRE")
        data = json.loads(request.httprequest.data)
        _logger.warning(data)

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

            init_time = datetime.now()
            request_time = datetime(init_time.year,init_time.month,init_time.day,init_time.hour,init_time.minute,init_time.second)
            expired_time = request_time + timedelta(seconds=tokens['expires_in'])

            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token', tokens['access_token'])
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_refresh_token', tokens['refresh_token'])
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_user_id', tokens['user_id'])
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_is_connect', True)
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_valido', True)
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_request_time', request_time)
            request.env['ir.config_parameter'].set_param('ctt_mercado_libre.mercado_libre_token_expires', expired_time)

            cron = request.env['ir.cron'].create({
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

        server_action = request.env.ref("ctt_mercado_libre.redirect_settings_action")
        return request.redirect(
            '/web#action=%s&model=res.config.settings' % (server_action.id))