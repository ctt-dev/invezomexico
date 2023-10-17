# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    marketplace_template_ids = fields.One2many(
        'marketplaces.template',
        'product_id',
        string='Plantillas'
    )