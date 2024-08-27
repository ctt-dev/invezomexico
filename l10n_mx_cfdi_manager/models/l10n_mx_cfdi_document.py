# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging
import io
import base64
from odoo.http import request, route
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescarga, VerificaSolicitudDescarga, DescargaMasiva, Validacion
from lxml.objectify import fromstring

class l10n_mx_cfdi_document(models.Model):
    _name = 'l10n_mx.cfdi_document'
    _description = 'Modelo de documentos'
    _order = 'id desc'
    
    name = fields.Char(
        related="uuid"
    )
    
    cfdi_request=fields.Many2one(
        'l10n_mx.cfdi_request',
        string="Solicitud CFDI"
    )
    uuid=fields.Char(
        string="UUID*"
    )
    partner_id=fields.Many2one(
        'res.partner',
        string="ID de socio"
    )
    cfdi_state=fields.Char(
        string="Estado CFDI"
    )
    attatch=fields.Binary(
        string="Adjunto"
    )
    attatch_name=fields.Char(
        string="Nombre del archivo"
    )
    company_id=fields.Many2one(
        'res.company',
        string="ID de compañía"
    )
    rfc_emisor=fields.Char(
        string="RFC Emisor"
    )
    emisor=fields.Char(
        string="Emisor"
    )
    rfc_receptor=fields.Char(
        string="RFC Receptor"
    )
    total=fields.Float(
        string="Total"
    )
    metadata=fields.Text(
        string="Metadata"
    )
    def compute_move_id(self):
        for rec in self:
            move_id = False
            for move in rec.moves_ids:
                move_id = move.id
            rec.move_id = move_id
    move_id = fields.Many2one(
        'account.move',
        string="Factura relacionada",
        compute=compute_move_id
    )
    moves_ids=fields.One2many(
        'account.move',
        'cfdi_document',
        string="Facturas relacionadas"
    ) 
    date=fields.Date(
        string="Fecha"
    )
    
    metadata_pretty = fields.Text(
        string="Metadata pretty",
        compute='_pretty_xml_data'
    )
    
    folio = fields.Char(
        string="Folio"
    )
    
    link_state = fields.Selection([
        ('link', 'Vinculado'),
        ('unlink', 'No vinculado')],
        default='unlink',
        compute="_is_doc_linked",
        store=True
    )
    
    type_comprobante = fields.Selection(
        [
            ('I', 'Ingreso'),
            ('E', 'Egreso'),
            ('T', 'Traslado'),
            ('P', 'Pago'),
            ('N', 'Nomina')
        ],
        string="Tipo de documento",
        default="I"
    )
    
    xml_path = fields.Char(
        compute='_get_full_path'
    )
    
    get_cfdi_state = fields.Boolean(
        string="¿Obtener estado de CFDI?",
        default=False
    )

    journal_id = fields.Many2one(
        'account.journal',
        string="Diario"
    )

    pdf_preview=fields.Binary(
        string="Previsualización PDF"
    )

    pdf_preview_name=fields.Char(
        string="Nombre del archivo - Previsualización PDF"
    )

    def generate_pdf_preview(self):
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_report', [self.id])[0]
        self.pdf_preview = base64.b64encode(pdf)
        self.pdf_preview_name = self.name+".pdf"
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documento CFDI',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_form').id,
            'res_model': 'l10n_mx.cfdi_document',
            'res_id': self.id,
            'target': 'new',
        }
        
    def compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.env['res.currency'].search([('name','=',rec.get_cfdi_data('Moneda'))])
    currency_id = fields.Many2one(
        'res.currency',
        compute=compute_currency_id
    )
    
    def _get_full_path(self):    
        for rec in self:
            rec.xml_path = '/home/odoo/data/filestore/CFDI/{}'.format(rec.cfdi_request.id_solicitud)
    
    @api.depends('moves_ids','moves_ids.state','moves_ids.name')
    def _is_doc_linked(self):
        for rec in self:
            if len(rec.moves_ids) > 0:
                rec.link_state = 'link'
            else:
                rec.link_state = 'unlink'
    
    def _pretty_xml_data(self):
        for rec in self:
            xml_data = minidom.parseString(rec.metadata)
            rec.metadata_pretty = xml_data.toprettyxml()
    
    def _extract_metada(self):
        for rec in self:
            with io.BytesIO(base64.b64decode(self.attatch)) as xml_data:
                xml = minidom.parse(xml_data)
                self.write({
                    'metadata':xml.toxml()
                })
    
    def verify_state(self):            
        validacion = Validacion()
        estado = validacion.obtener_estado(self.rfc_emisor, self.rfc_receptor, str(self.total), self.uuid)
        self.write({
            'cfdi_state': estado['estado'],
            'get_cfdi_state': False
        })
        
    def automated_cfdi_state(self):
        cfdi_documents = self.env['l10n_mx.cfdi_document'].search([])
        for document in cfdi_documents:
            document.verify_state()
    
    def name_get(self):
        result = []
        for document in self:
            result.append((document.id,document.uuid))
        return result
        
    def _read_cfdi(self,data):
        with io.BytesIO(base64.b64decode(data)) as xml_data:
            xml = minidom.parse(xml_data)
            
            REF = ""
            if str(xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Serie')) != "":
                REF += str(xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Serie'))
                if str(xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Folio')) != "":
                    REF += "-"
            if str(xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Folio')) != "":
                REF += str(xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Folio'))
                
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
            MONEDA = xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('Moneda')
            
            validacion = Validacion()
            estado = validacion.obtener_estado(RFC_EMISOR, RFC_RECEPTOR, TOTAL, UUID)
            
            return {
                'uuid': UUID,
                'cfdi_state': estado['estado'],
                'rfc_emisor': RFC_EMISOR,
                'emisor': EMISOR,
                'rfc_receptor': RFC_RECEPTOR,
                'total': float(TOTAL),
                'date': DATE,
                'metodo_pago': METODO_PAGO,
                'conceptos':CONCEPTOS,
                'folio': FOLIO,
                'type': TYPE_C,
                'ref': REF,
                'moneda': MONEDA
            }
        
    def show_bill(self):
        if self.move_id.id:
            return {
                'name':'Asientos contables',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(False,'form')],
                'res_model':'account.move',
                'view_id':self.env.ref('account.view_move_form').id,
                'type':'ir.actions.act_window',
                'res_id':self.move_id.id,
                'target':'current',
                'context': "{'edit':1}",
            }
        
    def show_document(self):
        if self.id:
            return {
                'name':'Documento CFDI',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(False,'form')],
                'res_model':'l10n_mx.cfdi_document',
                'view_id':self.env.ref('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_form').id,
                'type':'ir.actions.act_window',
                'res_id':self.id,
                'target':'current',
                'context': "{'edit':1}",
            }
        
    def create_bill_showing_new_record(self):
        new_moves = self.env['account.move']
        for rec in self:
            new_moves += rec.create_bill()
        
        # # raise ValidationError(len(new_moves))
        if len(new_moves) == 1:
            return {
                'name':'Asientos contables',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(False,'form')],
                'res_model':'account.move',
                'view_id':self.env.ref('account.view_move_form').id,
                'type':'ir.actions.act_window',
                'res_id':new_moves[0].id,
                'target':'current',
                'context': "{'edit':1}",
            }
        elif len(new_moves) > 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Asientos Contables',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': self.env.ref('account.view_in_invoice_tree').id,
                'res_model': 'account.move',
                'views': [(False, 'tree'),(False, 'form')],
                'context': "{'edit':1}",
                'domain': [('id','in',new_moves.ids)],
                'target': 'current',
            }

    def get_cfdi_data(self, attribute): 
        # Get data from cfdi:Comprobante and tfd:TimbreFiscalDigital sections
        metadata_pretty = str(self.metadata_pretty)
        index_1 = metadata_pretty.find(attribute)
        metadata_pretty_rest = metadata_pretty[index_1+len(attribute)+2:]
        index_2 = metadata_pretty_rest.find('"')
        if index_1 >= 0 and index_2 >= 0:
            return str(metadata_pretty_rest[0:index_2])
        else:
            return ""

    def get_cfdi_data_from_string(self, string, attribute):
        # Get data from cfdi:Comprobante and tfd:TimbreFiscalDigital sections
        metadata_pretty = str(string)
        index_1 = metadata_pretty.find(attribute)
        metadata_pretty_rest = metadata_pretty[index_1+len(attribute)+2:]
        index_2 = metadata_pretty_rest.find('"')
        return str(metadata_pretty_rest[0:index_2])

    def get_cfdi_conceptos_data(self):
        ## Get conceptos section
        metadata_pretty = str(self.metadata_pretty)
        index_1 = metadata_pretty.find("<cfdi:Conceptos>")
        index_2 = metadata_pretty.find("</cfdi:Conceptos>")
        conceptos_data = metadata_pretty[index_1+len("<cfdi:Conceptos>"):index_2]
        
        conceptos_list = []
        break_loop = False
        c = 0
        ## Get data from each concept
        while break_loop == False:
            c += 1
            final_len = ("</cfdi:Concepto>")
            concepto_index_1 = conceptos_data.find("<cfdi:Concepto")
            concepto_index_2 = conceptos_data.find("</cfdi:Concepto>",concepto_index_1)
            concepto_data = conceptos_data[concepto_index_1+len("<cfdi:Concepto"):concepto_index_2+len("</cfdi:Concepto>")]
            if concepto_index_2 < 0:
                concepto_index_2 = conceptos_data.find("/>",concepto_index_1)
                concepto_data = conceptos_data[concepto_index_1+len("<cfdi:Concepto"):concepto_index_2+len("/>")]
                final_len = len("/>")
            # raise UserError(str(concepto_index_2))
            # if c == 2:
            #     raise UserError(str(concepto_data))

            ## Get impuestos section
            impuestos_index_1 = concepto_data.find("<cfdi:Impuestos>")
            impuestos_index_2 = concepto_data.find("</cfdi:Impuestos>")
            impuestos_data = concepto_data[impuestos_index_1+len("<cfdi:Impuestos>"):impuestos_index_2]
            impuestos_list = []
            break_impuestos_loop = False
            ## Get data from each impuesto
            while break_impuestos_loop == False:
                impuesto_index_1 = impuestos_data.find("<cfdi:Traslado ")
                impuesto_index_2 = impuestos_data.find("/>")
                impuesto_data = impuestos_data[impuesto_index_1+len("<cfdi:Traslado "):impuesto_index_2+len("/>")]
                if impuesto_index_1 > 0:
                    impuestos_list.append(
                        dict({
                            'Base': self.get_cfdi_data_from_string(impuesto_data, "Base"),
                            'Impuesto': self.get_cfdi_data_from_string(impuesto_data, "Impuesto"),
                            'TipoFactor': self.get_cfdi_data_from_string(impuesto_data, "TipoFactor"),
                            'TasaOCuota': self.get_cfdi_data_from_string(impuesto_data, "TasaOCuota"),
                            'Importe': self.get_cfdi_data_from_string(impuesto_data, "Importe"),
                        })
                    )
                    impuestos_data = impuestos_data[impuesto_index_2+len("/>"):]
                    # raise UserError(str(impuestos_data))
                else:
                    break_impuestos_loop = True
            # raise UserError(str(impuestos_list))
            
            if concepto_index_1 > 0:
                conceptos_list.append(
                    dict({
                        'ClaveProdServ': self.get_cfdi_data_from_string(concepto_data, "ClaveProdServ"),
                        'NoIdentificacion': self.get_cfdi_data_from_string(concepto_data, "NoIdentificacion"),
                        'Cantidad': self.get_cfdi_data_from_string(concepto_data, "Cantidad"),
                        'Unidad': self.get_cfdi_data_from_string(concepto_data, "Unidad"),
                        'ClaveUnidad': self.get_cfdi_data_from_string(concepto_data, "ClaveUnidad"),
                        'Descripcion': self.get_cfdi_data_from_string(concepto_data, "Descripcion"),
                        'ValorUnitario': self.get_cfdi_data_from_string(concepto_data, "ValorUnitario"),
                        'Importe': self.get_cfdi_data_from_string(concepto_data, "Importe"),
                        'ObjetoImp': self.get_cfdi_data_from_string(concepto_data, "ObjetoImp"),
                        'Impuestos': impuestos_list
                    })
                )
                conceptos_data = conceptos_data[len(concepto_data)+len("<cfdi:Concepto"):] 
            else:
                break_loop = True
            # if c == 3:
            #     raise UserError(str(conceptos_data))
        return conceptos_list


    def get_cfdi_impuestos_data(self):
        ##Get all conceptos
        conceptos_list = self.get_cfdi_conceptos_data()
        impuestos_name_list = []
        impuestos_list = []
        for concepto in conceptos_list:
            for impuesto in concepto['Impuestos']:
                # raise UserError(str(impuesto))
                impuesto_name = str(impuesto['Impuesto']) + "-" + str(impuesto['TipoFactor']) + "-" + str(impuesto['TasaOCuota'])
                # raise UserError(str(impuesto_name))
                if impuesto_name not in impuestos_name_list:
                    impuestos_name_list.append(impuesto_name)

        for impuesto_name in impuestos_name_list:
            importe_total = 0
            base_total = 0
            for concepto in conceptos_list:
                for impuesto in concepto['Impuestos']:
                    if impuesto['Impuesto'] == impuesto_name[0:3] and impuesto['TipoFactor'] == impuesto_name[4:8] and impuesto['TasaOCuota'] == impuesto_name[9:17]:
                        base_total += float(impuesto['Base'])
                        importe_total += float(impuesto['Importe'])
            
            impuestos_list.append(
                dict({
                    'Base': base_total,
                    'Impuesto': impuesto_name[0:3],
                    'TipoFactor': impuesto_name[4:8],
                    'TasaOCuota': impuesto_name[9:17],
                    'Importe': importe_total,
                })
            )
        return impuestos_list

    def get_qr_section_data(self):
        cfdi_data = base64.decodebytes(self.attatch)
        return self.env['account.move']._l10n_mx_edi_decode_cfdi_etree(fromstring(cfdi_data))
        
    def create_bill(self):
        #Check if UUID is already linked
        partner_bills = self.env['account.move'].search([('cfdi_document.uuid','=',self.uuid)])
        if len(partner_bills) > 0:
            raise ValidationError("El UUID del documento que seleccionó ya se encuentra relacionado. Se recomienda revisar el listado de los documentos vinculados relacionados a el RFC ''" + str(self.rfc_emisor) + "'' para continuar...")
        
        data = self._read_cfdi(self.attatch)
        if data['rfc_receptor'] == self.env.company.vat:
            # partner = self.env['res.partner'].search([('vat','=',data['rfc_emisor']),('parent_id','=',False),('name','ilike',data['emisor'])], order='id desc', limit=1)
            partner = self.env['res.partner']
            partners = self.env['res.partner']
            partners += self.env['res.partner'].search([('vat','=',data['rfc_emisor']),('parent_id','=',False)])
            if len(partners) == 0:
                partners += self.env['res.partner'].search([('name','ilike',data['emisor']),('parent_id','=',False)])
            
            prev_invoice_count = 0
            for p in partners:
                if len(p.invoice_ids) >= prev_invoice_count:
                    partner = p
                    prev_invoice_count = len(p.invoice_ids)
                
            if len(partner) < 1:
                partner = self.env['res.partner'].create({
                    'name': data['emisor'],
                    'vat': data['rfc_emisor'],
                    'country_id': self.env['ir.model.data']._xmlid_to_res_id('base.mx')
                })
            payment_term = self.env['account.payment.term'].with_context(lang='es_MX').search([('name', '=', data['metodo_pago'])])
            if len(payment_term) == 0:
                if partner.property_supplier_payment_term_id.id:
                    payment_term = partner.property_supplier_payment_term_id

            currency_id = self.env['res.currency'].search([('name','=',data['moneda'])], limit=1)
            if len(currency_id) == 0:
                currency_id = self.env.company.currency_id

            journal_id = self.env.company.sat_account_incoming_journal_id.id if data['type'] == 'I' else self.env.company.sat_account_egress_journal_id.id
            if self.journal_id.id:
                journal_id = self.journal_id.id
                    
            account_move = self.env['account.move'].create({
                'partner_id': partner.id,
                'invoice_date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'state': 'draft',
                'move_type': 'in_invoice' if data['type'] == 'I' else 'in_refund',
                'extract_state': 'no_extract_requested',
                'journal_id': journal_id,
                'l10n_mx_edi_sat_status': 'undefined',
                'currency_id': currency_id.id,
                'invoice_payment_term_id': payment_term.id if payment_term else None,
                'cfdi_document': self.id,
                'ref': data['ref']
            })
            
            move_lines_list = self.env['account.move.line']

            lines = []
            
            if self.env.company.generation_type == "TC":
                for concepto in data['conceptos']:
                    importe = concepto.getAttribute('Importe') if concepto.getAttribute('Importe') != "" else 0
                    descuento = concepto.getAttribute('Descuento') if concepto.getAttribute('Descuento') != "" else 0
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
    #                     if float(base) != importe and concepto.getAttribute('Unidad') == 'Litro':
                        if round(float(base),2) != round(float(importe),2):
                            is_gasoline = True
                    for retencion in retenciones:
                        if traslado.getAttribute('TipoFactor') == 'Tasa':
                            rets.append(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))
                            
                    claveunidad = concepto.getAttribute('ClaveUnidad')
                    uom_id = self.env['uom.uom'].search([('unspsc_code_id.code','=',claveunidad)], limit=1)
                    
                    lines.append({
                        'importe':float(importe) - float(descuento),
                        'base': base,
                        'tasas': tasas if tasas else [],
                        'retenciones':rets if rets else [],
                        'is_gasoline':is_gasoline,
                        'description':concepto.getAttribute('Descripcion'),
                        'unidad': uom_id
                    })

                for line in lines:
                    if line['is_gasoline']:
                        tax_list = self.env['account.tax']
                        for imp in line['tasas']:
                            result = self.env['account.tax'].search([('amount','=',imp),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
                            tax_list += result
                        tax_list_zero = self.env['account.tax'].search([('amount','=',0),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                        if len(tax_list_zero) == 0:
                            raise UserError("No se encontraron impuestos registrados con base al 0.00%. Configurelo para continuar...")

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'],
                            'move_id': account_move.id,
                            'quantity':  1,
                            'price_unit': float(line['base']),
                            'tax_ids': tax_list.ids,
                            'journal_id': account_move.journal_id.id,
                            'account_id': account_move.journal_id.default_account_id.id,
                            'product_uom_id': line['unidad'].id
                        })
                        move_lines_list += move_line

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'] + " Tasa 0%",
                            'move_id': account_move.id,
                            'quantity':  1,
                            'price_unit': float(line['importe']) - float(line['base']),
                            'tax_ids': tax_list_zero.ids,
                            'journal_id': account_move.journal_id.id,
                            'account_id': account_move.journal_id.default_account_id.id,
                            'product_uom_id': line['unidad'].id
                        })
                        move_lines_list += move_line

                    else:
                        rets_id = []
                        tax_rets = self.env['account.tax']
                        tax_list = self.env['account.tax']
                        for ret in line['retenciones']:
                            result = self.env['account.tax'].search([('amount','=',ret),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No se encontraron retenciones registradas con base al " + "{:.4f}".format(ret) + "%. Configurela para continuar...")
                            tax_rets += result
                        for imp in line['tasas']:
                            result = self.env['account.tax'].search([('amount','=',imp),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No taxes registered with a base of " + "{:.4f}".format(imp) + "%. Create it to continue...")
                            tax_list += result
    #                     tax_rets = self.env['account.tax'].search([('id','in',rets_id),('active','=',True)], limit=1)

                        tax_list = tax_list + tax_rets

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'],
                            'move_id': account_move.id,
                            'quantity':  1,
                            'price_unit': float(line['importe']),
                            'tax_ids': tax_list.ids,
                            'journal_id': account_move.journal_id.id,
                            'account_id': account_move.journal_id.default_account_id.id,
                            'product_uom_id': line['unidad'].id
                        })
                        move_lines_list += move_line
                
            elif self.env.company.generation_type == "IG":
                m = ""
                for concepto in data['conceptos']:
                    importe = concepto.getAttribute('Importe') if concepto.getAttribute('Importe') != "" else 0
                    descuento = concepto.getAttribute('Descuento') if concepto.getAttribute('Descuento') != "" else 0
                    is_gasoline = False
                    base = 0.0
                    tasas = []
                    rets = []
                    traslados = concepto.getElementsByTagName('cfdi:Traslado')
                    retenciones = concepto.getElementsByTagName('cfdi:Retencion')
                    # name = "Saldo pendiente a "
                    name = "Outstanding balance "
                    for traslado in traslados:
                        base = traslado.getAttribute('Base')
                        if traslado.getAttribute('TipoFactor') == 'Tasa':
                            tasas.append(float(traslado.getAttribute('TasaOCuota'))*100)
                            name += "Tasa "+str(float(traslado.getAttribute('TasaOCuota'))*100)+", "
    #                     if float(base) != importe and concepto.getAttribute('Unidad') == 'Litro':
                        if round(float(base),2) != round(float(importe),2):
                            is_gasoline = True
                    for retencion in retenciones:
                        if traslado.getAttribute('TipoFactor') == 'Tasa':
                            rets.append(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))
                            name += "Retención "+str(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))+", "
                    check = False
                    for line in lines:
                        if line['ref'] == name:
                            line['importe'] += float(importe) - float(descuento)
                            line['base'] = float(line['base']) + float(base)
                            check = True
                    if check == False:
                        lines.append({
                            'ref':name[:-2],
                            'importe':float(importe) - float(descuento),
                            'base': base,
                            # 'tasas': tasas if tasas else [0.00],
                            # 'retenciones':rets if rets else [0.00],
                            'tasas': tasas if tasas else [],
                            'retenciones':rets if rets else [],
                            'is_gasoline':is_gasoline,
                            'description':name[:-2]
                        })
                # raise ValidationError(str(lines) + "\n" + str(m))

                for line in lines:
                    if line['is_gasoline']:
                        tax_list = self.env['account.tax']
                        for imp in line['tasas']:
                            result = self.env['account.tax'].search([('amount','=',imp),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
                            tax_list += result
                        tax_list_zero = self.env['account.tax'].search([('amount','=',0),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                        if len(tax_list_zero) == 0:
                            raise UserError("No se encontraron impuestos registrados con base al 0.00%. Configurelo para continuar...")

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'],
                            'move_id': account_move.id,
                            'quantity':  1,
                            'price_unit': float(line['base']),
                            'tax_ids': tax_list.ids,
                            'journal_id': account_move.journal_id.id,
                            'account_id': account_move.journal_id.default_account_id.id,
                        })
                        move_lines_list += move_line

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'] + " Tasa 0%",
                            'move_id': account_move.id,
                            'quantity':  1,
                            'price_unit': float(line['importe']) - float(line['base']),
                            'tax_ids': tax_list_zero.ids,
                            'journal_id': account_move.journal_id.id,
                            'account_id': account_move.journal_id.default_account_id.id,
                        })
                        move_lines_list += move_line

                    else:
                        rets_id = []
                        tax_rets = self.env['account.tax']
                        tax_list = self.env['account.tax']
                        for ret in line['retenciones']:
                            result = self.env['account.tax'].search([('amount','=',ret),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No se encontraron retenciones registradas con base al " + "{:.4f}".format(ret) + "%. Configurela para continuar...")
                            tax_rets += result
                        for imp in line['tasas']:
                            result = self.env['account.tax'].search([('amount','=',imp),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
                            tax_list += result
    #                     tax_rets = self.env['account.tax'].search([('id','in',rets_id),('active','=',True)], limit=1)

                        tax_list = tax_list + tax_rets

                        move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line['description'],
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
            return account_move
        else:
            raise UserError("El RFC receptor del documento XML no coincide con el RFC de la empresa")
            
            
    def action_download_xml(self):
        url = '/web/binary/download_document?tab_id=%s' % self.ids
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }
    
    def send_mail_for_state_change(self):
        for rec in self:
            email_to = []
            for user in rec.env.company.receiver_user_ids:
                email_to.append(user.login)
            rec.env.ref('l10n_mx_cfdi_manager.mail_template_cfdi_document_check').send_mail(
                rec.id,
                # email_layout_xmlid="mail.mail_notification_light",
                email_values={
                    'email_to': email_to,
                    'email_from': rec.env.company.sender_user_id.login,
                    'reply_to': rec.env.company.sender_user_id.login,
                    # 'author_id': self.partner_id.id,
                },
                force_send=True,
            )

    def show_preview(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documento CFDI',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_mx_cfdi_manager.l10n_mx_cfdi_document_form').id,
            'res_model': 'l10n_mx.cfdi_document',
            'res_id': self.id,
            'target': 'new',
        }