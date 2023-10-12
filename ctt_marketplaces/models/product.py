# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    marketplace_tamplate_ids = fields.One2many(
        'marketplaces.tamplate',
        'product_id',
        string='Plantillas'
    )