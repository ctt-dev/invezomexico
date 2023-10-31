# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CttWalmartCatgoryInstall(models.TransientModel):
    _name = 'walmart.category.install'

    categ_ids = fields.Many2many('marketplaces.category', string='Categorías')

    def install_categs(self):
        pass