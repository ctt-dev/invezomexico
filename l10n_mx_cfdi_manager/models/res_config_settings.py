# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError , UserError

class res_config_settings_inheritance(models.TransientModel):
    _inherit = 'res.config.settings'
 
    fiel_ids=fields.Many2many(
        'l10n_mx.cfdi_fiel',
        string="FIELES"
    )