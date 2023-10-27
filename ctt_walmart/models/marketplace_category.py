# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceTemplateCategory(models.Model):
    _inherit = 'marketplaces.category'

    is_installed = fields.Boolean(string='Instalado', default=False)
    group = fields.Char(string='Grupo')