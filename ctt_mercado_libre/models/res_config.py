# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CTTMELIResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
   
    app_id = fields.Char("App ID", config_parameter='ctt_mercado_libre.app_id')
    client_secret = fields.Char("Client secret", config_parameter='ctt_mercado_libre.client_secret')
    code = fields.Char("Code")