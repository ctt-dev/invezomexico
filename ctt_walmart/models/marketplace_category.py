# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MarketplaceTemplateCategory(models.Model):
    _inherit = 'marketplaces.category'

    # is_installed = fields.Boolean(string='Instalado', default=False)
    group = fields.Char(string='Grupo')

    # @api.model
    # def name_get(self):
    #     marketplace = self.env.ref("ctt_walmart.marketplace_walmart")
    #     result = []
    #     for record in self:
    #         if record.marketplace_id.id == marketplace.id:
    #             name = f'{record.group} / {record.name}'
    #         else:
    #             name = record.display_name
    #         result.append((record.id, name))
    #     return result