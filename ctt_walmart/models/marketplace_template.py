# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.ctt_walmart.utils.WalmartAPI import WalmartAPI

class MarketplaceProductTemplate(models.Model):
    _inherit = 'marketplaces.tamplate'

    def publish_walmart_item(self):
        pass