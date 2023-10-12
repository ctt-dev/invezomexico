# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceTemplateCategory(models.Model):
    _name = 'marketplaces.category'
    _description = 'Categorias para plantillas de marketplaces'

    name = fields.Char(string='Nombre')
    display_name = fields.Char(string='Nombre')
    attribute_ids = fields.One2many(
        'marketplaces.category.attribute',
        'category_id',
        string='Atributos de Categoría'
    )    

class MarketplaceCategoryAttribute(models.Model):
    _name = 'marketplaces.category.attribute'
    _description = 'Atributos de categorias de markeplaces'

    category_id = fields.Many2one('marketplaces.category', string='Categoría')
    name = fields.Char(string='Nombre')
    display_name = fields.Char(string='Nombre')
    required = fields.Boolean(string='Requerido', default=False)
    type = fields.Char(string='Tipo')

    
