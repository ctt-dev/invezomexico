# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CttWalmartConfigSettings(models.Model):
    _name = 'walmart.feed'
    _description = 'Modelo para seguimiento de peticiones a walmart'

    feedId = fields.Char(string='ID de petición')
    status = fields.Selection(selection=[
        ('RECEIVED','Recibido'),
        ('INPROGRESS','En progreso'),
        ('PROCESSED','Procesada'),
        ('ERROR', 'Error')
        ],string='Estado')
    template_id = fields.Many2one('marketplaces.template', string='Plantilla')