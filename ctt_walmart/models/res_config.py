# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CttWalmartConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
   
    walmart_client_id = fields.Char(string="Client ID", config_parameter='ctt_walmart.walmart_client_id')
    walmart_client_secret = fields.Char(string="Client secret", config_parameter='ctt_walmart.walmart_client_secret')
    walmart_category_count = fields.Integer('Numero de categorías', compute="_compute_walmart_categ_count", config_parameter='ctt_walmart.walmart_category_count')

    def _compute_walmart_categ_count(self):
        categ_count = self.env['marketplaces.category'].search_count([('is_installed', '=', True)])
        for rec in self:
            rec.walmart_category_count = categ_count