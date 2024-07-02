# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import os
import datetime
from datetime import timedelta
import pytz
import logging
import tempfile
import base64
import zipfile
import glob
import io
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescarga, VerificaSolicitudDescarga, DescargaMasiva, Validacion

_CFDI_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/CFDI/'

class wizard_manual_creation(models.TransientModel):
    _name = 'l10n_mx.wizard_manual_creation'
    _description = 'Wizard para crear CFDI manualmente'

    zip = fields.Binary(
        string="Archivo .ZIP" 
    )

    filename = fields.Char(
        string= "Nombre de Archivo .ZIP", 
        required=True
    )

    def show_import_notification(self,processed_files,imported_files):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ("Archivo ZIP procesado"),
                'type': 'info',
                'message': ("Documentos procesados: " + str(processed_files) + "\n\nDocumentos importados: " + str(imported_files)),
                'sticky': True,
             },
         }

    def process_zip(self):
        if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT):
            os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT)
        if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL"):
            os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL")

        #Create folder for ZIP/RAR
        now = datetime.datetime.now()
        folder_name = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)
        if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name):
            os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name)

        #Save ZIP/RAR on folder
        with open(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name + "/" + self.filename, 'wb+') as f:
            f.write(base64.b64decode(self.zip))

        #Extract ZIP/RAR
        with zipfile.ZipFile(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name + "/" + self.filename, 'r') as zip_ref:
            zip_ref.extractall(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name + "/")

        cfdi_documents_count_prev = self.env['l10n_mx.cfdi_document'].search_count([])

        #Create CFDI documents
        xml_files = glob.glob(_CFDI_DOWNLOAD_PATH_ROOT + "MANUAL/" + folder_name + "/*.xml")
        [self.env['l10n_mx.cfdi_request'].create_doc(file_path) for file_path in xml_files]
        
        cfdi_documents_count_post = self.env['l10n_mx.cfdi_document'].search_count([])

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ("Archivo ZIP procesado"),
                'type': 'info',
                'message': ("Documentos importados: " + str(cfdi_documents_count_post-cfdi_documents_count_prev) + " / " + str(len(xml_files))),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': 'Documentos',
                    'view_type': 'tree',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_tree').id,
                    'res_model': 'l10n_mx.cfdi_document',
                    'views': [(False, 'tree'),(False, 'form')],
                    'context': "{'edit':0}",
                    'domain': [('create_date','>=',now)],
                    'target': 'current',
                }
             },
         }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Documentos',
        #     'view_type': 'tree',
        #     'view_mode': 'tree',
        #     'view_id': self.env.ref('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_tree').id,
        #     'res_model': 'l10n_mx.cfdi_document',
        #     'views': [(False, 'tree'),(False, 'form')],
        #     'context': "{'edit':0}",
        #     'domain': [('create_date','>=',now)],
        #     'target': 'current',
        # }