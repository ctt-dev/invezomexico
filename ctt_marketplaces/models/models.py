# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ctt_marketplaces(models.Model):
#     _name = 'ctt_marketplaces.ctt_marketplaces'
#     _description = 'ctt_marketplaces.ctt_marketplaces'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
