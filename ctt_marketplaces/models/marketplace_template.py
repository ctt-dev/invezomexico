# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceProductTemplate(models.Model):
    _name = 'marketplaces.tamplate'
    _description = 'Plantilla para productos en marketplaces'

    marketplace = fields.Selection(selection=[],string='Marketplace')

    #Campos genericos para templates
    marketplace_id = fields.Char(string='Marketplace ID')
    marketplace_title = fields.Char(string='Titulo', size=60)
    marketplace_description = fields.Text(string='Descripción')

    #Lineas para campos especificos de marketplaces
    # field_lines = fields.One2many(
    #     'marketplaces.tamplate.field.line',
    #     'template_id',
    #     string='Campos generales de plantilla'
    # )

    #Campos de categoria del producto
    marketplace_categ_id = fields.Many2one('marketplaces.category', string='Categoría')

# class MarketplaceTemplateField(models.Model):
#     _name = 'marketplaces.tamplate.field'
#     _description = 'Campos para productos en marketplace'

#     name = fields.Char(string='Nombre')
#     display_name = fields.Char(string='Campo')
#     required = fields.Boolean(string='Requerido', default=False)
#     type = fields.Char(string='Tipo')

# class MarketplaceTemplateFieldLine(models.Model):
#     _name = 'marketplaces.tamplate.field.line'
#     _description = 'Lineas para campos del template'

#     template_id = fields.Many2one('marketplaces.tamplate', string='Plantilla')
#     field_id = fields.Many2one('marketplaces.template.field', string='Campos')
#     value = fields.Char(string='Valor')