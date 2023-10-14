# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Marketplace(models.Model):
    _name = 'marketplaces.marketplace'
    _description = 'Descripcion de MarketPlace'

    name = fields.Char(string='Nombre')
    field_ids = fields.One2many(
        'marketplaces.marketplace.field',
        'marketplace_id',
        string='Campos de Marketplace'
    )

class MarketplaceField(models.Model):
    _name = 'marketplaces.marketplace.field'
    _description = 'Campos para productos en marketplace'

    name = fields.Char(string='Nombre')
    display_name = fields.Char(string='Campo')
    required = fields.Boolean(string='Requerido', default=False)
    type = fields.Char(string='Tipo')
    complex_type = fields.Char(string='Tipo Complejo')
    marketplace_id = fields.Many2one('marketplaces.marketplace', string='Marketplace')