# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceProductTemplate(models.Model):
    _name = 'marketplaces.tamplate'
    _description = 'Plantilla para productos en marketplaces'

    marketplace = fields.Selection(selection=[],string='Marketplace')
    mkt_id = fields.Many2one('marketplaces.marketplace', string='Marketplace')
    product_id = fields.Many2one('product.template', string='Producto')

    #Campos genericos para templates
    marketplace_id = fields.Char(string='Marketplace ID')
    marketplace_title = fields.Char(string='Titulo', size=60)
    marketplace_description = fields.Text(string='Descripción')

    #Lineas para campos especificos de marketplaces
    field_lines = fields.One2many(
        'marketplaces.field.line',
        'template_id',
        string='Campos generales de plantilla'
    )

    #Campos de categoria del producto
    marketplace_categ_id = fields.Many2one('marketplaces.category', string='Categoría')
    attr_lines = fields.One2many(
        'marketplaces.attribute.line',
        'template_id',
        string='Campos de categoría'
    )

    def test_button(self):
        pass
        
class MarketplaceTemplateFieldLine(models.Model):
    _name = 'marketplaces.field.line'
    _description = 'Lineas para campos del template'

    template_id = fields.Many2one('marketplaces.tamplate', string='Plantilla')
    field_id = fields.Many2one('marketplaces.marketplace.field', string='Campo')
    value = fields.Char(string='Valor')

class MarketplaceTemplateFieldLine(models.Model):
    _name = 'marketplaces.attribute.line'
    _description = 'Lineas para campos del template'

    template_id = fields.Many2one('marketplaces.tamplate', string='Plantilla')
    attr_id = fields.Many2one('marketplaces.category.attribute', string='Campo')
    value = fields.Char(string='Valor')