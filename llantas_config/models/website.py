from odoo import models, fields, api, _
import logging
import json
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
import datetime

class website_inherit(models.Model):
    _inherit = 'website'
    _description='website_inherit'
    
    def _get_ancho_sort_mapping(self):
        _logger.warning('serie')
        atributos = self.env['product.attribute'].search([('name','=','Tamaño Ancho')])
        array = []
        for rec in atributos.value_ids:
            array.append((atributos.id, str(atributos.id)+'-'+str(rec.id), rec.name))
        return array
    
    
    def _get_rin_sort_mapping(self):
        self.ensure_one()
        _logger.warning('serie')
        atributos = self.env['product.attribute'].search([('name','=','Tamaño Rin')])
        array = []
        for rec in atributos.value_ids:
            array.append((atributos.id, str(atributos.id)+'-'+str(rec.id), rec.name))
        return array

    
    def _get_alto_sort_mapping(self):
        atributos = self.env['product.attribute'].search([('name','=','Tamaño Alto')])
        array = []
        for rec in atributos.value_ids:
            array.append((atributos.id, str(atributos.id)+'-'+str(rec.id), rec.name))
        return array


    
    
    def llamar_controlador(self):
        # Puedes personalizar la ruta según tu configuración
        url = '/TomarValoresSelectP'
        response = self.env['http.request'].httprequest(url, type='http', method='GET')
        # Puedes manejar la respuesta según tus necesidades
        _logger.warning(response.text)



