# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CttWalmartConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
   
    walmart_client_id = fields.Char(string="Client ID", config_parameter='ctt_walmart.walmart_client_id')
    walmart_client_secret = fields.Char(string="Client secret", config_parameter='ctt_walmart.walmart_client_secret')