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
    
    @staticmethod
    def _get_ancho_sort_mapping():
        _logger.warning('anchos')
        return [
            ('Anchos', _('Anchos')),
            ('7', _('7')),
            ('7.5', _('7.5')),
            ('8', _('8')),
            ('8.75', _('8.75')),
            ('9.5', _('9.5')),
            ('10', _('10')),
            ('11', _('11')),
            ('12', _('12')),
            ('13', _('13')),
            ('25', _('25')),
            ('26', _('26')),
            ('27', _('27')),
            ('28', _('28')),
            ('29', _('29')),
            ('30', _('30')),
            ('31', _('31')),
            ('32', _('32')),
            ('33', _('33')),
            ('34', _('34')),
            ('35', _('35')),
            ('37', _('37')),
            ('38', _('38')),
            ('115', _('115')),
            ('125', _('125')),
            ('145', _('145')),
            ('155', _('155')),
            ('165', _('165')),
            ('175', _('175')),
            ('185', _('185')),
            ('195', _('195')),
            ('205', _('205')),
            ('215', _('215')),
            ('225', _('225')),
            ('235', _('235')),
            ('245', _('245')),
            ('255', _('255')),
            ('265', _('265')),
            ('275', _('275')),
            ('285', _('285')),
            ('295', _('295')),
            ('305', _('305')),
            ('315', _('315')),
            ('325', _('325')),
            ('335', _('335')),
            ('345', _('345')),
            ('355', _('355')),
            ('385', _('385')),
        ]
    
    
    @staticmethod
    def _get_serie_sort_mapping():
        _logger.warning('serie')
        return [
            ('Series', _('Series')),
            ('8.5', _('8.5')),
            ('9', _('9')),
            ('9.5', _('9.5')),
            ('10', _('10')),
            ('10.5', _('10.5')),
            ('11', _('11')),
            ('11.5', _('11.5')),
            ('12', _('12')),
            ('12.5', _('12.5')),
            ('13.5', _('13.5')),
            ('15.5', _('15.5')),
            ('25', _('25')),
            ('30', _('30')),
            ('35', _('35')),
            ('40', _('40')),
            ('45', _('45')),
            ('50', _('50')),
            ('55', _('55')),
            ('60', _('60')),
            ('65', _('65')),
            ('70', _('70')),
            ('75', _('75')),
            ('80', _('80')),
            ('85', _('85')),
            ('100', _('100')),
        ]
        
    @staticmethod
    def _get_diametro_sort_mapping():
        _logger.warning('Diametro')
        return [
            ('Diametro', _('Diametro')),
            ('R12', _('R12')),
            ('R13', _('R13')),
            ('R14', _('R14')),
            ('R15', _('R15')),
            ('R16', _('R16')),
            ('R16.5', _('R16.5')),
            ('R17', _('R17')),
            ('R17.5', _('R17.5')),
            ('R18', _('R18')),
            ('R19', _('R19')),
            ('R19.5', _('R19.5')),
            ('R20', _('R20')),
            ('R21', _('R21')),
            ('R22', _('R22')),
            ('R22.5', _('R22.5')),
            ('R23', _('R23')),
            ('R24', _('R24')),
            ('R24.5', _('R24.5')),
        ]


    
    
    def llamar_controlador(self):
        # Puedes personalizar la ruta según tu configuración
        url = '/TomarValoresSelectP'
        response = self.env['http.request'].httprequest(url, type='http', method='GET')
        # Puedes manejar la respuesta según tus necesidades
        _logger.warning(response.text)



