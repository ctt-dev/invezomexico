# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import os
import datetime
import pytz
import logging
import tempfile
import base64
import zipfile
import glob
import io
import csv
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescargaEmitidos, VerificaSolicitudDescarga, DescargaMasiva, Validacion
from cfdiclient.solicitadescargaRecibidos import SolicitaDescargaRecibidos

from satcfdi.models import Signer
from satcfdi.pacs.sat import SAT, TipoDescargaMasivaTerceros, EstadoSolicitud, EstadoComprobante

_CFDI_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/CFDI/'
_METADATA_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/METADATA/'

class l10n_mx_cfdi_request(models.Model):
    _name = 'l10n_mx.cfdi_request'
    _description = 'Modelo de solicitud'
    _order = 'id desc'

    @api.depends('id_solicitud','name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = str(rec.id_solicitud) if rec.id_solicitud else "/"
    
    # def name_get(self):
    #     res = super(l10n_mx_cfdi_request, self).name_get()
    #     data = []
    #     for e in self:
    #         display_value = e.id_solicitud
    #         data.append((e.id, display_value))
    #     return data

    @api.depends('name')
    def compute_name(self):
        for rec in self:
            rec.name = rec.id_solicitud
    name = fields.Char(
        string="UUID",
        compute=compute_name,
        store=True
    )
    
    id_solicitud=fields.Char(
        string="ID Solicitud"
    )
    paquetes=fields.Char(
        string="Paquetes"
    )
    start_date=fields.Date(
        string="Fecha de inicio"
    )
    end_date=fields.Date(
        string="Fecha de terminación"
    )
    rfc_consultant=fields.Char(
        string="RFC consultante"
    )
    rfc_receptor=fields.Char(
        string="RFC receptor"
    )
    rfc_emmiter=fields.Char(
        string="RFC emisor"
    )
    type_emision = fields.Selection(
        [
            ('R', 'Recibido'),
            ('E', 'Emitido'),
        ],
        string="Tipo de emisión",
        default="R"
    )
    state=fields.Selection(
        [
            ('0','Token inválido'),
            ('1','Aceptada'),
            ('2','En proceso'),
            ('3','Terminada'),
            ('4','Error'),
            ('5','Rechazada'),
            ('6','Vencida'),
        ],
        string="Estado"
    )
    done=fields.Boolean(
        string="Listo",
        default=False
    )
    
    docs_create = fields.Boolean(
        string="Documentos listos",
        default=False
    )
    
    cfdi_documents=fields.One2many(
        'l10n_mx.cfdi_document',
        'cfdi_request',
        string="Documentos CFDI"
    )
    metadata_lines = fields.One2many(
        'l10n_mx.cfdi_metadata',
        'request_id',
        string="Lineas de metadatos"
    )
    attatch=fields.Binary(
        string="Adjunto"
    )
    company_id=fields.Many2one(
        'res.company',
        string="ID de compañía"
    )
    total_documents=fields.Integer(
        string="No. Documentos"
    )

    request_type = fields.Selection(
        [
            ('CFDI','CFDI'),
            ('Metadata','METADATA')
        ], 
        string="Tipo de solicitud",
        default="CFDI"
    )
    
    @api.onchange("company_id")
    def _auto_fill_rfc(self):
        for record in self:
            record.rfc_consultant = record.company_id.vat
            record.rfc_receptor = record.company_id.vat

    def decode_base64(self, data):
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return base64.b64decode(data)
    
    @api.model
    def create(self,values):
        record = super(l10n_mx_cfdi_request, self).create(values)
        
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',record.company_id.id)])
        
        if not keys_id:
            raise UserError("No se encontraron llaves de la compañia")
        if record.company_id.python_api == 'cfdiclient':
            fiel = self._read_fiel(keys_id)
            session = self._create_new_seassion(fiel)
            estado_comprobante = 'Vigente'
            if record.request_type == 'Metadata':
                estado_comprobante = 'Todos'
            if record.type_emision == 'R':
                # Recibidos
                descarga = SolicitaDescargaRecibidos(fiel)
                result = descarga.solicitar_descarga(session, record.rfc_consultant, record.start_date, record.end_date, rfc_receptor=record.rfc_receptor, tipo_solicitud=record.request_type, estado_comprobante=estado_comprobante)
            elif record.type_emision == 'E':
                # Emitidos
                descarga = SolicitaDescargaEmitidos(fiel)
                result = descarga.solicitar_descarga(session, record.rfc_consultant, record.start_date, record.end_date, rfc_emisor=record.rfc_receptor, tipo_solicitud=record.request_type, estado_comprobante=estado_comprobante)
            
            _logger.warning(result)
    
            # {'mensaje': 'Solicitud Aceptada', 'cod_estatus': '5000', 'id_solicitud': 'be2a3e76-684f-416a-afdf-0f9378c346be'}
            
            record.write({
                'id_solicitud':result['id_solicitud']
            })
            
            record.verificar_solicitud()
        elif record.company_id.python_api == 'satcfdi':
            _logger.warning('PETICION SATCFDI')
            # # Decodificar los binarios
            # cer_bytes = self.decode_base64(keys_id.clave)
            # key_bytes = self.decode_base64(keys_id.fiel)
            # password = keys_id.serial_number
            
            # # Crear firmante y SAT service
            # signer = Signer.load(
            #     certificate=cer_bytes,
            #     key=key_bytes,
            #     password=password
            # )
            
            # sat_service = SAT(
            #     signer=signer
            # )

            sat_service = self._get_SAT_CFDI_service(keys_id)
            response = False
            tipo_solicitud = TipoDescargaMasivaTerceros.CFDI
            if record.request_type == 'Metadata':
                tipo_solicitud = TipoDescargaMasivaTerceros.METADATA
            if record.type_emision == 'R':
                # Facturas Recibidas
                response = sat_service.recover_comprobante_received_request(
                    fecha_inicial=record.start_date,
                    fecha_final=record.end_date,
                    rfc_receptor=record.rfc_receptor,
                    tipo_solicitud=tipo_solicitud,
                    estado_comprobante=EstadoComprobante.VIGENTE 
                )
            elif record.type_emision == 'E':
                response = sat_service.recover_comprobante_emitted_request(
                    fecha_inicial=record.start_date,
                    fecha_final=record.end_date,
                    rfc_emisor=record.rfc_receptor,
                    tipo_solicitud=tipo_solicitud,
                    estado_comprobante=EstadoComprobante.VIGENTE 
                )
            _logger.warning(str(response))
            # Revisar estado de descarga
            response_for_status = sat_service.recover_comprobante_status(str(response['IdSolicitud']))
            _logger.warning(str(response_for_status))
            
            record.write({
                'id_solicitud':response['IdSolicitud'],
                # 'paquetes': ','.join(response_for_status['IdsPaquetes']),
                # 'state': str(response_for_status['EstadoSolicitud']),
                # 'total_documents': int(response_for_status['NumeroCFDIs'])
            })
            
            record.verificar_solicitud()
        return record
    
    def _read_fiel(self,keys_id):
        file_path = tempfile.gettempdir()+'/keyfile.key'
        f = open(file_path,'wb')
        f.write(base64.decodebytes(keys_id.fiel))
        f.close()
        key_der = open(file_path, 'rb').read()
#         raise UserError(key_der)
        
        file_path = tempfile.gettempdir()+'/cerfile.cer'
        f = open(file_path,'wb')
        f.write(base64.decodebytes(keys_id.clave))
        f.close()
        cer_der = open(file_path, 'rb').read()
#         raise UserError(cer_der)
        fiel = Fiel(cer_der, key_der, keys_id.serial_number)
        return fiel
    
    def _create_new_seassion(self,fiel):
        auth = Autenticacion(fiel)
        token = auth.obtener_token()
        return token

    def _get_SAT_CFDI_service(self, keys_id=None):
        # Decodificar los binarios
        cer_bytes = self.decode_base64(keys_id.clave)
        key_bytes = self.decode_base64(keys_id.fiel)
        password = keys_id.serial_number
        
        # Crear firmante y SAT service
        signer = Signer.load(
            certificate=cer_bytes,
            key=key_bytes,
            password=password
        )
        
        sat_service = SAT(
            signer=signer
        )

        return sat_service

    def _read_cfdi(self,data):
        with io.BytesIO(base64.b64decode(data)) as xml_data:
            xml = minidom.parse(xml_data)
            
            UUID = xml.getElementsByTagName('tfd:TimbreFiscalDigital')[0].getAttribute('UUID')
            EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Nombre')
            RFC_EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Rfc')
            RFC_RECEPTOR = xml.getElementsByTagName('cfdi:Receptor')[0].getAttribute('Rfc')
            DATE = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Fecha').split('T')
            METODO_PAGO = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('CondicionesDePago')
            CONCEPTOS = xml.getElementsByTagName('cfdi:Concepto')
            FOLIO = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Folio')
            TYPE_C = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('TipoDeComprobante')
            PUE_PPD = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('MetodoPago')
            TOTAL = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Total')
            if TYPE_C == 'P':
                if len(xml.getElementsByTagName('pago20:Pago')) > 0:
                    TOTAL = xml.getElementsByTagName('pago20:Pago')[0].getAttribute('Monto')
                if len(xml.getElementsByTagName('Pago20:Pago')) > 0:
                    TOTAL = xml.getElementsByTagName('Pago20:Pago')[0].getAttribute('Monto')
                if len(xml.getElementsByTagName('pago10:Pago')) > 0:
                    TOTAL = xml.getElementsByTagName('pago10:Pago')[0].getAttribute('Monto')
                if len(xml.getElementsByTagName('Pago10:Pago')) > 0:
                    TOTAL = xml.getElementsByTagName('Pago10:Pago')[0].getAttribute('Monto')
            
            return {
                'uuid': UUID,
#                 'cfdi_state': estado['estado'],
                'rfc_emisor': RFC_EMISOR,
                'emisor': EMISOR,
                'rfc_receptor': RFC_RECEPTOR,
                'total': float(TOTAL),
                'date': DATE,
                'metodo_pago': METODO_PAGO,
                'conceptos': CONCEPTOS,
                'folio': FOLIO,
                'type': TYPE_C,
                'pue_ppd': PUE_PPD
            }
    
    def verificar_solicitud(self):
        # raise UserError(self.company_id.python_api)
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',self.company_id.id)])

        if not keys_id:
            raise UserError("No se encontraron llaves de la compañia")
        
        if self.company_id.python_api == 'cfdiclient':
            _logger.warning(f'VERIFICAR CFDICLIENT')
            fiel = self._read_fiel(keys_id)
            v_descarga = VerificaSolicitudDescarga(fiel, timeout=100)
            session = self._create_new_seassion(fiel)
            
            try:
                result = v_descarga.verificar_descarga(session, self.rfc_consultant, self.id_solicitud)
                _logger.warning(result)
                self.write({
                    'paquetes': ','.join(result['paquetes']),
                    'state': result['estado_solicitud'],
                    'total_documents': int(result['numero_cfdis'])
                })
            except:
                # continue
                raise ValidationError("La petición no pudo verificarse correctamente, revise sus credenciales y RFC")
            # {'estado_solicitud': '3', 'numero_cfdis': '8', 'cod_estatus': '5000', 'paquetes': ['a4897f62-a279-4f52-bc35-03bde4081627_01'], 'codigo_estado_solicitud': '5000', 'mensaje': 'Solicitud Aceptada'}

        elif self.company_id.python_api == 'satcfdi':
            _logger.warning(f'VERIFICAR SATCFDI')
            # Decodificar los binarios
            cer_bytes = self.decode_base64(keys_id.clave)
            key_bytes = self.decode_base64(keys_id.fiel)
            password = keys_id.serial_number
            
            # Crear firmante y SAT service
            signer = Signer.load(
                certificate=cer_bytes,
                key=key_bytes,
                password=password
            )
            
            sat_service = SAT(
                signer=signer
            )
            # sat_service = self._get_SAT_CFDI_service(keys_id)

            try:
                response_for_status = sat_service.recover_comprobante_status(self.id_solicitud)
                _logger.warning(response_for_status)
                self.write({
                    'paquetes': ','.join(response_for_status['IdsPaquetes']),
                    'state': str(response_for_status['EstadoSolicitud']),
                    'total_documents': int(response_for_status['NumeroCFDIs'])
                })
            
            except:
                # continue
                raise ValidationError("La petición no pudo verificarse correctamente, revise sus credenciales y RFC")
        
    # def descargar_paquetes(self):
    #     if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT):
    #         os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT)

    #     if not os.path.exists(_METADATA_DOWNLOAD_PATH_ROOT):
    #         os.makedirs(_METADATA_DOWNLOAD_PATH_ROOT)
            
    #     if self.request_type == "CFDI":
    #         if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT + self.id_solicitud):
    #             os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT + self.id_solicitud)
    #     elif self.request_type == 'Metadata':
    #         if not os.path.exists(_METADATA_DOWNLOAD_PATH_ROOT + self.id_solicitud):
    #             os.makedirs(_METADATA_DOWNLOAD_PATH_ROOT + self.id_solicitud)
        
    #     paquetes = self.paquetes.split(',')
        
    #     keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',self.company_id.id)])
    #     fiel = self._read_fiel(keys_id)
    #     session = self._create_new_seassion(fiel)
    #     for paquete in paquetes:
    #         descarga = DescargaMasiva(fiel)
    #         descarga = descarga.descargar_paquete(session, self.rfc_consultant, paquete)
    #         if self.request_type == 'CFDI':
    #             if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete)):
    #                 with open(_CFDI_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete), 'wb') as fp:
    #                     if descarga['paquete_b64'] != None:
    #                         fp.write(base64.b64decode(descarga['paquete_b64']))
    #         elif self.request_type.request_type == 'Metadata':
    #             if not os.path.exists(_METADATA_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete)):
    #                 with open(_METADATA_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete), 'wb') as fp:
    #                     if descarga['paquete_b64'] != None:
    #                         fp.write(base64.b64decode(descarga['paquete_b64']))

    #     self.write({
    #         'done':True
    #     })

    def descargar_paquetes(self):
        # Crear directorios raíz si no existen
        os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT, exist_ok=True)
        os.makedirs(_METADATA_DOWNLOAD_PATH_ROOT, exist_ok=True)
    
        # Determinar ruta de descarga según tipo de solicitud
        if self.request_type == "CFDI":
            root_path = _CFDI_DOWNLOAD_PATH_ROOT
        elif self.request_type == "Metadata":
            root_path = _METADATA_DOWNLOAD_PATH_ROOT
        else:
            raise UserError("Tipo de solicitud no reconocido: %s" % self.request_type)
    
        solicitud_path = os.path.join(root_path, self.id_solicitud)
        os.makedirs(solicitud_path, exist_ok=True)
    
        # Obtener llaves
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id', '=', self.company_id.id)], limit=1)
        if not keys_id:
            raise UserError("No se encontraron llaves para la compañía.")

        paquetes = self.paquetes.split(',')

        if self.company_id.python_api == 'cfdiclient':
            fiel = self._read_fiel(keys_id)
            session = self._create_new_seassion(fiel)
        
            # Descargar paquetes
            descarga = DescargaMasiva(fiel)
        
            for paquete in paquetes:
                resultado = descarga.descargar_paquete(session, self.rfc_consultant, paquete)
                b64_data = resultado.get('paquete_b64')
        
                if b64_data:
                    file_path = os.path.join(solicitud_path, f"{paquete}.zip")
                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as fp:
                            fp.write(base64.b64decode(b64_data))
        elif self.company_id.python_api == 'satcfdi':
            # Decodificar los binarios
            cer_bytes = self.decode_base64(keys_id.clave)
            key_bytes = self.decode_base64(keys_id.fiel)
            password = keys_id.serial_number
            
            # Crear firmante y SAT service
            signer = Signer.load(
                certificate=cer_bytes,
                key=key_bytes,
                password=password
            )
            
            sat_service = SAT(
                signer=signer
            )
            # Revisar estado de descarga
            response = sat_service.recover_comprobante_status(self.id_solicitud)
            for id_paquete in paquetes:
                try:
                    response, paquete_b64 = sat_service.recover_comprobante_download(id_paquete=id_paquete)
        
                    if response.get("CodEstatus") == "5008":
                        _logger.warning(f"El paquete {id_paquete} ha alcanzado el límite de descargas.")
                        continue
        
                    if paquete_b64:
                        paquete_bin = base64.b64decode(paquete_b64)
                        ruta_zip = os.path.join(_CFDI_DOWNLOAD_PATH_ROOT, self.id_solicitud, f"{id_paquete}.zip")
                        if not os.path.exists(ruta_zip):
                            with open(ruta_zip, 'wb') as fp:
                                fp.write(paquete_bin)
                except Exception as e:
                    _logger.error(f"Error al descargar el paquete {id_paquete}: {str(e)}")
    
        # Marcar como completado
        self.write({'done': True})
        
    def create_doc(self,file_path):
        try:
            file = open(file_path,"rb")
            data = base64.b64encode(file.read())
            file_name = file_path.split("/")[-1]
    
            file_data = self._read_cfdi(data)

            company_id = self.env.user.company_id.id
            if self.company_id.id:
                company_id = self.company_id.id
            company_ids = self.env['res.company'].search([('vat','=',file_data['rfc_receptor'])])
            if len(company_ids) > 0:
                company_id = company_ids[0].id
            
            #Check if exists, if exists avoid creation...
            document_ids = self.env['l10n_mx.cfdi_document'].search([('uuid','=',file_data['uuid'])])
            if len(document_ids) == 0:
                type_emision = "R"
                if file_data['rfc_emisor'] == self.env.company.vat:
                    type_emision = 'E'
                if file_data['rfc_receptor'] == self.env.company.vat or file_data['rfc_emisor'] == self.env.company.vat and self.env.company.id == company_id:
                    document = self.env['l10n_mx.cfdi_document'].create({
                        'cfdi_request': self.id,
                        'company_id': company_id,
                        'attatch': data,
                        'attatch_name': file_name,
                        'uuid': file_data['uuid'],
        #                     'cfdi_state': file_data['cfdi_state'],
                        'rfc_emisor': file_data['rfc_emisor'],
                        'emisor': file_data['emisor'],
                        'rfc_receptor': file_data['rfc_receptor'],
                        'total': file_data['total'],
                        'date': datetime.datetime.strptime(file_data['date'][0],'%Y-%m-%d'),
                        'folio': file_data['folio'],
                        'type_comprobante': file_data['type'],
                        'type_emision': type_emision,
                        'metodo_pago': file_data['pue_ppd'],
                    })
        
                    document._extract_metada()
        except:
            pass
        
    
    def create_request_documents(self):
        paquetes = self.paquetes.split(',')
        for paquete in paquetes:
            with zipfile.ZipFile(_CFDI_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete), 'r') as zip_ref:
                zip_ref.extractall(_CFDI_DOWNLOAD_PATH_ROOT+'{}/'.format(self.id_solicitud))
        
        xml_files = glob.glob(_CFDI_DOWNLOAD_PATH_ROOT+ self.id_solicitud + '/*.xml')
        # raise UserError(xml_files)
        [self.create_doc(file_path) for file_path in xml_files]
            
        self.write({
            'docs_create':True
        })

    def create_request_metadata(self):
        paquetes = self.paquetes.split(',')
        extract_path = os.path.join(_METADATA_DOWNLOAD_PATH_ROOT, self.id_solicitud)

        for paquete in paquetes:
            zip_path = os.path.join(extract_path, f"{paquete}.zip")
            if os.path.isfile(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                    _logger.info(f"ZIP extraído: {zip_path}")
            else:
                _logger.warning(f"No se encontró el archivo ZIP: {zip_path}")
        
        self._process_metadata_txt_files(extract_path)
        
        self.write({
            'docs_create':True
        })

    def _process_metadata_txt_files(self, folder_path):
        txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]
        Metadata = self.env['l10n_mx.cfdi_metadata']
        records_to_create = []

        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                reader = csv.reader(txt_file, delimiter='~')
                next(reader, None)  # Omitir encabezado

                for row in reader:
                    if len(row) < 12:
                        continue

                    records_to_create.append({
                        'name': row[0].strip(),
                        'rfc_emisor': row[1].strip(),
                        'nombre_emisor': row[2].strip().strip('"'),
                        'rfc_receptor': row[3].strip(),
                        'nombre_receptor': row[4].strip(),
                        'rfc_pac': row[5].strip(),
                        'date': self._parse_datetime(row[6]),
                        'cert_date': self._parse_datetime(row[7]),
                        'total': float(row[8].strip() or 0),
                        'type_comprobante': row[9].strip(),
                        'state': row[10].strip(),
                        'cancel_date': self._parse_datetime(row[11]) if len(row) > 11 else False,
                        'request_id': self.id,
                    })

        if records_to_create:
            Metadata.create(records_to_create)

    def _parse_datetime(self, value):
        value = value.strip()
        return fields.Datetime.from_string(value) if value else False
        
    def automated_verification(self):
        
        solicitudes = self.env['l10n_mx.cfdi_request'].search([('state','in',['0','1','2'])])
        
        for solicitud in solicitudes:
            solicitud.verificar_solicitud()
            
    def automated_download(self):
        
        solicitudes = self.env['l10n_mx.cfdi_request'].search(['&',('state','=','3'),('done','=',False)])
        
        for solicitud in solicitudes:
            solicitud.descargar_paquetes()

    
    def _automated_request(self, request_type='CFDI', request_days=1):
        _logger.warning("Accion planificada")
        _logger.warning(f'request_type: {request_type}')
        
        fiels = self.env['l10n_mx.cfdi_fiel'].search([])
        
        for fiel in fiels:
            date_end = datetime.datetime.now().date()
            date_delta = datetime.timedelta(days=request_days)
            data = {
                'company_id':fiel.company_id.id,
                'rfc_consultant': fiel.company_id.vat, 
                'rfc_receptor': fiel.company_id.vat,
                'start_date': date_end - date_delta,
                'end_date': date_end,
                'request_type': request_type
            }
            request = self.env['l10n_mx.cfdi_request'].create(data)

    def automated_daily_request(self):
        self._automated_request(request_type='CFDI',request_days=1)

    def automated_metadata_request(self):
        self._automated_request(request_type='Metadata',request_days=90)
        
    def create_bill(self, document):
        data = self._read_cfdi(document.attatch)
        if data['rfc_receptor'] == self.env.company.vat:
            partner = self.env['res.partner'].search([('vat','=',data['rfc_emisor']),('is_company','=',True)])
            if not partner:
                try:
                    partner = self.env['res.partner'].create({
                        'name': data['emisor'],
                        'vat': data['rfc_emisor']
                    })
                except:
                    pass
            payment_term = self.env['account.payment.term'].with_context(lang='es_MX').search([('name', '=', data['metodo_pago'])])
            account_move = self.env['account.move'].create({
                'invoice_date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'state': 'draft',
                'move_type': 'in_invoice' if data['type'] == 'I' else 'in_refund',
                'extract_state': 'no_extract_requested',
                'journal_id': self.env.company.sat_account_incoming_journal_id.id if data['type'] == 'I' else self.env.company.sat_account_egress_journal_id.id,
                'l10n_mx_edi_sat_status': 'undefined',
                'currency_id': self.env.company.currency_id.id,
                'invoice_payment_term_id': payment_term.id if payment_term else None,
                'cfdi_document': document.id
            })
            
            move_lines_list = self.env['account.move.line']

            lines = []
            
            for concepto in data['conceptos']:
                importe = concepto.getAttribute('Importe')
                is_gasoline = False
                base = 0.0
                tasas = []
                rets = []
                traslados = concepto.getElementsByTagName('cfdi:Traslado')
                retenciones = concepto.getElementsByTagName('cfdi:Retencion')
                for traslado in traslados:
                    base = traslado.getAttribute('Base')
                    if traslado.getAttribute('TipoFactor') == 'Tasa':
                        tasas.append(float(traslado.getAttribute('TasaOCuota'))*100)
                    if float(base) != importe and concepto.getAttribute('Unidad') == 'Litro':
                        is_gasoline = True
                for retencion in retenciones:
                    if traslado.getAttribute('TipoFactor') == 'Tasa':
                        rets.append(round(-float(retencion.getAttribute('TasaOCuota'))*100,2))
                lines.append({
                    'importe':importe,
                    'base': base,
                    'tasas': tasas if tasas else [0.00],
                    'retenciones':rets if rets else [0.00],
                    'is_gasoline':is_gasoline,
                    'description':concepto.getAttribute('Descripcion')
                })
                
            for line in lines:
                if line['is_gasoline']:
                    tax_list = self.env['account.tax'].search(['&',('amount','in',line['tasas']),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id)])
                    
                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + line['description'] + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['base']),
                        'tax_ids': tax_list.ids,
                        'journal_id': account_move.journal_id.id,
                        'account_id': account_move.journal_id.default_account_id.id,
                    })
                    move_lines_list += move_line

                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + ''.format(float(line['importe'])-float(line['base'])) + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['importe']) - float(line['base']),
                        'tax_ids': [9],
                        'journal_id': account_move.journal_id.id,
                        'account_id': account_move.journal_id.default_account_id.id,
                    })
                    move_lines_list += move_line
                    
                else:
                    rets_id = []
                    for ret in line['retenciones']:
                        if ret == -4.00:
                            rets_id.append(3)
                        elif ret == -10.00:
                            rets_id.append(4)
                        elif ret == -10.67:
                            rets_id.append(8)
                    tax_list = self.env['account.tax'].search(['&',('amount','in',line['tasas']),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id)])
                    tax_rets = self.env['account.tax'].search([('id','in',rets_id)])

                    tax_list = tax_list + tax_rets

                    move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'name': "Saldo pendiente " + line['description'] + " Tasa",
                        'move_id': account_move.id,
                        'quantity':  1,
                        'price_unit': float(line['importe']),
                        'tax_ids': tax_list.ids,
                        'journal_id': account_move.journal_id.id,
                        'account_id': account_move.journal_id.default_account_id.id,
                    })
                    move_lines_list += move_line
                
            account_move.with_context(check_move_validity=False).write({
                'invoice_line_ids':move_lines_list.ids,
            })
                
            diferencia = data['total']-account_move.amount_total
            if  diferencia == 0:
                account_move.message_post(
                    body='FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total)
                    )
                )
            else:
                account_move.message_post(
                    body = 'FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b> \nDiferencia: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total),
                        '{:20,.2f}'.format(abs(diferencia))
                    )
                )

    def name_get(self):
        result = []
        for request in self:
            result.append((request.id,request.id_solicitud))
        return result

    def create_failure_request(self):
        xml_folders = glob.glob(_CFDI_DOWNLOAD_PATH_ROOT + "*/", recursive = True)
        
        for folder in xml_folders:
            id_solicitud = folder.split('/')[-2]
            solicitud = self.env['l10n_mx.cfdi_request'].search([('id_solicitud','like',id_solicitud)])
            
            if not solicitud:
                peticion = self.env['l10n_mx.cfdi_request'].create({
                    'id_solicitud':id_solicitud,
                    'rfc_consultant': self.env.company.vat,
                    'rfc_receptor': self.env.company.vat,
                    'state':'3',
                    'company_id':self.env.company.id,
                    'done':True,
                    'docs_create':False,
                })

    def create_documents_from_zip(self, folder, filename):
        with zipfile.ZipFile(_CFDI_DOWNLOAD_PATH_ROOT + 'MANUAL/{}/{}'.format(folder, filename), 'r') as zip_ref:
            zip_ref.extractall(_CFDI_DOWNLOAD_PATH_ROOT+'MANUAL/{}/'.format(folder))
            
        xml_files = glob.glob(_CFDI_DOWNLOAD_PATH_ROOT + 'MANUAL/{}/*.xml'.format(folder))
        [self.create_doc(file_path) for file_path in xml_files]