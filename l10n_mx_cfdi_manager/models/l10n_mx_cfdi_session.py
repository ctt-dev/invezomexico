# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging
import tempfile
import base64
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

from cfdiclient import Autenticacion, Fiel

class l10n_mx_cfdi_session(models.Model):
    _name = 'l10n_mx.cfdi_session'
    # _description = 'Modelo de sesión'
    _description = 'Sessión'
    _order = 'id desc'
    
    
    name=fields.Char(
        string="Token"
    )
    company_id=fields.Many2one(
        'res.partner',
        # string="ID de compañía"
        string="Company"
    )
    
    @api.model
    def create(self,values):
        record = super(l10n_mx_cfdi_session, self).create(values)
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',record.company_id.id)])
        
        file_path = tempfile.gettempdir()+'/keyfile.key'
        f = open(file_path,'wb')
        f.write(base64.decodebytes(keys_id.fiel))
        f.close()
        key_der = open(file_path, 'rb').read()
        
        file_path = tempfile.gettempdir()+'/cerfile.cer'
        f = open(file_path,'wb')
        f.write(base64.decodebytes(keys_id.clave))
        f.close()
        cer_der = open(file_path, 'rb').read()
        
        fiel = Fiel(cer_der, key_der, keys_id.serial_number)

        auth = Autenticacion(fiel)

        token = auth.obtener_token()
           
        record.write({ 
            'name': token
        })
        return record