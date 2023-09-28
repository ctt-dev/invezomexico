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

class res_company_inheritance(models.Model):
    _inherit = 'res.company'
    # _description = 'Modelo para agregar los certificados'
    _description = 'Company'
    
    fiel_ids=fields.One2many(
        'l10n_mx.cfdi_fiel',
        'company_id',
        string="FIEL"
    )
    
    sat_account_incoming_journal_id = fields.Many2one(
        'account.journal',
        # string = 'Diario de proveedores',
        string = 'Vendor Journal',
        domain = "[('type','=','purchase')]"
    )
    
    sat_account_egress_journal_id = fields.Many2one(
        'account.journal',
        # string = 'Diario de notas de credito'
        string = 'Credit notes Journal'
    )
    
    product_unspsc_code_for_gasoline = fields.Many2many(
        'product.unspsc.code',
        # string="Códigos SAT para combustibles"
        string="SAT codes for GAS and OIL"
    )
    
    dif_allowed = fields.Float(
        # string="Variación permitida para vinculación de CFDI",
        string="Allowed variation for CFDI vinculation",
        digits=(0,2),
        default=0.05,
        required=1
    )
    
    generation_type = fields.Selection(
        [
            # ('TC','Todos los conceptos'),
            ('TC','Every invoice line'),
            # ('IG','Impuestos Globales'),
            ('IG','Global taxes'),
        ],
        # string="Tipo de generación",
        string="Generation type",
        default="TC",
        required=1
    )
    
    days_for_status_check = fields.Integer(
        # string="Número de días para revisar vigencias",
        string="Number of days for state revision",
        default=3,
        required=1
    )
    
    sender_user_id = fields.Many2one(
        'res.users',
        # string="Usuario emisor"
        string="Sender user"
    )
    
    receiver_user_ids = fields.Many2many(
        'res.users',
        # string="Usuarios remitentes"
        string="Receiver users"
    )
    
#     @api.onchange('fiel_ids')
#     def read_cer_file(self):
#         file_path = tempfile.gettempdir()+'/cerfile.cer'
#         f = open(file_path,'wb')
#         f.write(base64.decodestring(self.fiel_ids[0].clave))
#         f.close()
#         cer_der = open(file_path, 'rb').read()
        
#         cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cer_der)
#         certIssue = cert.get_issuer()
        
#         datetime_struct_from = parser.parse(cert.get_notBefore().decode("UTF-8"))
#         datetime_struct = parser.parse(cert.get_notAfter().decode("UTF-8"))
        
#         raise UserError(datetime_struct.strftime('%Y-%m-%d %H:%M:%S'))