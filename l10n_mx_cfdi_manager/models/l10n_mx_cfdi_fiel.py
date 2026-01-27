# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging

import tempfile
import base64


import OpenSSL
import time
from dateutil import parser

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

class l10n_mx_cfdi_fiel(models.Model):
    _name = 'l10n_mx.cfdi_fiel'
    _description = 'Modelo de la FIEL'
    
    company_id=fields.Many2one(
        'res.company',
        string="Compañía"
    )
    fiel=fields.Binary(
        string="FIEL"
    )
    fiel_name=fields.Char(
        string="Nombre archivo Fiel"
    )
    clave=fields.Binary(
        string="Clave"
    )
    clave_name=fields.Char(
        string="Nombre archivo Clave"
    )
    emition_date=fields.Date(
        string="Fecha de emisión"
    )
    expiration_date=fields.Date(
        string="Fecha de expiración"
    )
    serial_number=fields.Char(
        string="Numero serial"
    )
    
    @api.constrains('fiel_name')
    def _check_fiel_name(self):
        if self.fiel:
            if not self.fiel:
                raise ValidationError(("There is no file"))
            else:
                # Check the file's extension
                tmp = self.fiel_name.split('.')
                ext = tmp[len(tmp)-1]
                if ext != 'key':
                    raise ValidationError(("The file must be a key file"))
    
    
    @api.onchange('clave')
    def read_cer_file(self):
        if self.clave != False:
            try:
                file_path = tempfile.gettempdir()+'/cerfile.cer'
                f = open(file_path,'wb')
                f.write(base64.decodebytes(self.clave))
                f.close()
                cer_der = open(file_path, 'rb').read()

                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cer_der)
                certIssue = cert.get_issuer()

                datetime_struct_from = parser.parse(cert.get_notBefore().decode("UTF-8"))
                datetime_struct_to = parser.parse(cert.get_notAfter().decode("UTF-8"))

                self.emition_date = datetime_struct_from.strftime('%Y-%m-%d %H:%M:%S')
                self.expiration_date = datetime_struct_to.strftime('%Y-%m-%d %H:%M:%S')
            except:
                raise ValidationError(("Error al leer el archivo"))