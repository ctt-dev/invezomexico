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
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescarga, VerificaSolicitudDescarga, DescargaMasiva, Validacion

_CFDI_DOWNLOAD_PATH_ROOT = '/home/odoo/data/filestore/CFDI/'

class l10n_mx_cfdi_request(models.Model):
    _name = 'l10n_mx.cfdi_request'
    _description = 'Modelo de solicitud'
    _order = 'id desc'
    
    
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
    
    @api.onchange("company_id")
    def _auto_fill_rfc(self):
        for record in self:
            record.rfc_consultant = record.company_id.vat
            record.rfc_receptor = record.company_id.vat

    @api.model
    def create(self,values):
        record = super(l10n_mx_cfdi_request, self).create(values)
        
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',record.company_id.id)])
        
        if not keys_id:
            raise UserError("No se encontraron llaves de la compañia")
            
        fiel = self._read_fiel(keys_id)
        session = self._create_new_seassion(fiel)
        
        descarga = SolicitaDescarga(fiel)
        # Recibidos
        result = descarga.solicitar_descarga(session, record.rfc_consultant, record.start_date, record.end_date, rfc_receptor=record.rfc_receptor, tipo_solicitud='CFDI')
        
        _logger.warning(result)

        # {'mensaje': 'Solicitud Aceptada', 'cod_estatus': '5000', 'id_solicitud': 'be2a3e76-684f-416a-afdf-0f9378c346be'}
        
        record.write({
            'id_solicitud':result['id_solicitud']
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

    def _read_cfdi(self,data):
        with io.BytesIO(base64.b64decode(data)) as xml_data:
            xml = minidom.parse(xml_data)
            
            UUID = xml.getElementsByTagName('tfd:TimbreFiscalDigital')[0].getAttribute('UUID')
            EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Nombre')
            RFC_EMISOR = xml.getElementsByTagName('cfdi:Emisor')[0].getAttribute('Rfc')
            RFC_RECEPTOR = xml.getElementsByTagName('cfdi:Receptor')[0].getAttribute('Rfc')
            TOTAL = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Total')
            DATE = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Fecha').split('T')
            METODO_PAGO = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('CondicionesDePago')
            CONCEPTOS = xml.getElementsByTagName('cfdi:Concepto')
            FOLIO = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Folio')
            TYPE_C = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('TipoDeComprobante')
            
#             validacion = Validacion()
#             estado = validacion.obtener_estado(RFC_EMISOR, RFC_RECEPTOR, TOTAL, UUID)
            
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
                'type': TYPE_C
            }
    
    def verificar_solicitud(self):
        
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',self.company_id.id)])

        fiel = self._read_fiel(keys_id)
        
        v_descarga = VerificaSolicitudDescarga(fiel, timeout=1000)
        
        session = self._create_new_seassion(fiel)
        try:
            result = v_descarga.verificar_descarga(session, self.rfc_consultant, self.id_solicitud)
        except:
            raise ValidationError("La petición no pudo verificarse correctamente, revise sus credenciales y RFC")
        self.write({
            'paquetes': ','.join(result['paquetes']),
            'state': result['estado_solicitud'],
            'total_documents': int(result['numero_cfdis'])
        })
        # {'estado_solicitud': '3', 'numero_cfdis': '8', 'cod_estatus': '5000', 'paquetes': ['a4897f62-a279-4f52-bc35-03bde4081627_01'], 'codigo_estado_solicitud': '5000', 'mensaje': 'Solicitud Aceptada'}
        
    def descargar_paquetes(self):
        if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT):
            os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT)
            
        if not os.path.exists(_CFDI_DOWNLOAD_PATH_ROOT + self.id_solicitud):
            os.makedirs(_CFDI_DOWNLOAD_PATH_ROOT + self.id_solicitud)
        paquetes = self.paquetes.split(',')
        
        keys_id = self.env['l10n_mx.cfdi_fiel'].search([('company_id','=',self.company_id.id)])
        fiel = self._read_fiel(keys_id)
        session = self._create_new_seassion(fiel)
        for paquete in paquetes:
            descarga = DescargaMasiva(fiel)
            descarga = descarga.descargar_paquete(session, self.rfc_consultant, paquete)
            with open(_CFDI_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete), 'wb') as fp:
                fp.write(base64.b64decode(descarga['paquete_b64']))
            with zipfile.ZipFile(_CFDI_DOWNLOAD_PATH_ROOT + '{}/{}.zip'.format(self.id_solicitud,paquete), 'r') as zip_ref:
                zip_ref.extractall(_CFDI_DOWNLOAD_PATH_ROOT+'{}/'.format(self.id_solicitud))

        self.write({
            'done':True
        })
        
    def create_doc(self,file_path):
        try:
            file = open(file_path,"rb")
            data = base64.b64encode(file.read())
            file_name = file_path.split("/")[-1]
    
            file_data = self._read_cfdi(data)
    
            company_id = self.env.company.id
            if self.company_id.id:
                company_id = self.company_id.id
            
            #Check if exists, if exists avoid creation...
            document_ids = self.env['l10n_mx.cfdi_document'].search([('uuid','=',file_data['uuid'])])
            if len(document_ids) == 0:
                if file_data['rfc_receptor'] == self.env.company.vat:
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
                    })
        
                    document._extract_metada()
        except:
            pass
        
    
    def create_request_documents(self):
        xml_files = glob.glob(_CFDI_DOWNLOAD_PATH_ROOT+ self.id_solicitud + '/*.xml')
        [self.create_doc(file_path) for file_path in xml_files]
            
        self.write({
            'docs_create':True
        })
        
    def automated_verification(self):
        
        solicitudes = self.env['l10n_mx.cfdi_request'].search([('state','<=','2')])
        
        for solicitud in solicitudes:
            solicitud.verificar_solicitud()
            
    def automated_download(self):
        
        solicitudes = self.env['l10n_mx.cfdi_request'].search(['&',('state','=','3'),('done','=',False)])
        
        for solicitud in solicitudes:
            solicitud.descargar_paquetes()
            
    def automated_request(self):
        fiels = self.env['l10n_mx.cfdi_fiel'].search([])
        
        for fiel in fiels:
            date_end = datetime.datetime.now().date()
            date_delta = datetime.timedelta(days=1)
            data = {
                'company_id':fiel.company_id.id,
                'rfc_consultant': fiel.company_id.vat, 
                'rfc_receptor': fiel.company_id.vat,
                'start_date': date_end - date_delta,
                'end_date': date_end
            }
            request = self.env['l10n_mx.cfdi_request'].create(data)
        
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
                
#                 xml_files = glob.glob(folder+ '/*.xml')
#                 [self.create_doc(file_path) for file_path in xml_files]
                