from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime
import urllib.request 
import json  

class marca_llanta(models.Model):
    _name = 'llantas_config.marca_llanta'
    _description = 'Catalogo de marca de llantas'
    _order = 'id desc'
    
    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=True)

class modelo_llanta(models.Model):
    _name = 'llantas_config.modelo_llanta'
    _description = 'Catalogo de modelo de llantas'
    _order = 'id desc'
    
    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=True)

class medida_llanta(models.Model):
    _name = 'llantas_config.medida_llanta'
    _description = 'Catalogo de medida de llantas'
    _order = 'id desc'

    name = fields.Char(string="Nombre",required=False)
    color = fields.Integer(string="Color",required=True)

# class status(models.Model):
#     _name = 'llantas_config.status'
#     _description = 'Status'
#     _order = 'id desc'
    
#     name = fields.Char(
#         string="Nombre",
#         required=True,
#         tracking=True,
#     )
    
#     color = fields.Integer(
#         string="Color",
#         tracking=True,
#     )
#     description=fields.Char(
#         string="Descripción",
#         tracking=True,
#     )
    
class almacen(models.Model):
    _name = 'llantas_config.almacen'
    _description = 'Catalogo de almacenes'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre",required=False)
    proveedor=fields.Many2one(
        "res.partner",
        string="Proveedor",
    )
    color = fields.Integer(string="Color",required=True)

class marketplaces(models.Model):
    _name = 'llantas_config.marketplaces'
    _description = 'Catalogo de marketplaces'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        company_dependent=True,
    )
    
    url= fields.Char(
        string="Url marketplace",
        company_dependent=True,
    )

    mostrar_comision=fields.Boolean(
        string="Mostrar comisión?",
        default="1",
        company_dependent=True,
    )
    
    mostrar_envio=fields.Boolean(
        string="Mostrar envio?",
        default="1",
        company_dependent=True,
    )

    category_id=fields.Many2one(
        "res.partner.category",
        string="Categoria contacto",
        company_dependent=True,
        
    )

    diarios_id=fields.Many2one(
        "account.journal",
        string="Diario de facturación",
        company_dependent=True,
    )
    
    color = fields.Integer(
        string="Color",
        company_dependent=True,
    )

    # def process_link(self):
    #     url = urllib.request.urlopen(self.url) 
    #     data = json.loads(url.read().decode()) 
    #     for x in data["objects"]["ResponseRow"]:
    #         self.env['llantas_config.ctt_tiredirect_cargar'].create({
    #             'description_description': x["Descripcion_Description"],
    #             'clave_parte': x["Clave_Parte"],
    #             'moneda_currency': x["Moneda_Currency"],
    #             'TC': x["TC"],
    #             'ES': x["ES"],
    #             'FS': x["FS"]
    #         })
    #     return {
    #         'name': 'Cargar existencias',
    #         'view_type': 'tree',
    #         'view_mode': 'tree',
    #         'view_id': self.env.ref('llantas_config.view_tiredirect_tree_cargar').id,
    #         'res_model': 'llantas_config.ctt_tiredirect_cargar',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #     }
        
class proveedores_link(models.Model):
    _name = 'llantas_config.proveedores_links'
    _description = 'Links proveedores'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
    )
    
    url= fields.Char(
        string="Url proveedor",
    )
    
    color = fields.Integer(
        string="Color",
    )
    company_id=fields.Many2one(
        "res.company",
        string="Empresa",
    )

    def process_link(self):
            url = urllib.request.urlopen(self.url) 
            data = json.loads(url.read().decode()) 
            for x in data["objects"]["ResponseRow"]:
                self.env['llantas_config.ctt_tiredirect_cargar'].create({
                    'description_description': x["Descripcion_Description"],
                    'clave_parte': x["Clave_Parte"],
                    'moneda_currency': x["Moneda_Currency"],
                    'TC': x["TC"],
                    'ES': x["ES"],
                    'FS': x["FS"],
                    'Existencia_Stock': x["Existencia_Stock"],
                })
            return {
                'name': 'Cargar existencias',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': self.env.ref('llantas_config.view_tiredirect_tree_cargar').id,
                'res_model': 'llantas_config.ctt_tiredirect_cargar',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

class status_ventas(models.Model):
    _name = 'llantas_config.status_ventas'
    _description = 'Catalogo de status'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        required=True,

    )
    
    description=fields.Char(
        string="Descripción",

    )
    
    color = fields.Integer(
        string="Color",
        required=True,
        
    )

class carriers(models.Model):
    _name = 'llantas_config.carrier'
    _description = 'Catalogo carriers'
    _order = 'id desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Nombre",
        required=True,
    )
