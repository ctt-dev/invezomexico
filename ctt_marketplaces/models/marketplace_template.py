# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceProductTemplate(models.Model):
    _name = 'marketplaces.template'
    _description = 'Plantilla para productos en marketplaces'

    marketplace = fields.Selection(selection=[],string='Marketplace')
    mkt_id = fields.Many2one('marketplaces.marketplace', string='Marketplace')
    mkt_name = fields.Char(related='mkt_id.name')
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

    @api.onchange('mkt_id')
    def _load_marketplace_fields(self):
        self.field_lines.unlink()

        required_fields = self.env['marketplaces.marketplace.field'].search([("marketplace_id","=",self.mkt_id.id),("required","=",True)])

        mkt_fields = []

        for field in required_fields:
            mkt_fields.append((0,0,{'field_id': field.id}))
        
        if mkt_fields:
            self.field_lines = mkt_fields
    
    @api.onchange('marketplace_categ_id')
    def _load_category_attrs(self):
        self.attr_lines.unlink()

        required_attrs = self.env['marketplaces.category.attribute'].search([("category_id","=",self.marketplace_categ_id.id),("required","=",True)])

        categ_attrs = []

        for attr in required_attrs:
            categ_attrs.append((0,0,{'attr_id': attr.id}))
        
        if categ_attrs:
            self.attr_lines = categ_attrs
        
class MarketplaceTemplateFieldLine(models.Model):
    _name = 'marketplaces.field.line'
    _description = 'Lineas para campos del template'

    template_id = fields.Many2one('marketplaces.template', string='Plantilla')
    field_id = fields.Many2one('marketplaces.marketplace.field', string='Campo')
    value = fields.Char(string='Valor')

class MarketplaceTemplateFieldLine(models.Model):
    _name = 'marketplaces.attribute.line'
    _description = 'Lineas para campos del template'

    template_id = fields.Many2one('marketplaces.template', string='Plantilla')
    attr_id = fields.Many2one('marketplaces.category.attribute', string='Campo')
    value = fields.Char(string='Valor')