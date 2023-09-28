# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime
import pytz
import logging
import io
import base64
from xml.dom import minidom
from xml.etree import ElementTree
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError
from cfdiclient import Autenticacion, Fiel, SolicitaDescarga, VerificaSolicitudDescarga, DescargaMasiva, Validacion

class l10n_mx_cfdi_document(models.Model):
    _name = 'l10n_mx.cfdi_document'
    # _description = 'Modelo de documentos'
    _description = 'CFDI document'
    _order = 'id desc'
    
    name = fields.Char(
        related="uuid"
    )
    
    cfdi_request=fields.Many2one(
        'l10n_mx.cfdi_request',
        # string="Solicitud CFDI"
        string="CFDI Reques"
    )
    uuid=fields.Char(
        string="UUID"
    )
    partner_id=fields.Many2one(
        'res.partner',
        # string="ID de socio"
        string="Partner"
    )
    cfdi_state=fields.Char(
        # string="Estado CFDI"
        string="CFDI state"
    )
    attatch=fields.Binary(
        # string="Adjunto"
        string="Attachment"
    )
    attatch_name=fields.Char(
        # string="Nombre del archivo"
        string="Filename"
    )
    company_id=fields.Many2one(
        'res.company',
        # string="ID de compañía"
        string="Company"
    )
    rfc_emisor=fields.Char(
        # string="RFC Emisor"
        string="Emiter RFC"
    )
    emisor=fields.Char(
        # string="Emisor"
        string="Emiter"
    )
    rfc_receptor=fields.Char(
        # string="RFC Receptor"
        string="Receptor RFC"
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
        # string="Factura relacionada",
        string="Journal entry",
        compute=compute_move_id
    )
    moves_ids=fields.One2many(
        'account.move',
        'cfdi_document',
        # string="Facturas relacionadas"
        string="Journal entries"
    ) 
    date=fields.Date(
        # string="Fecha"
        string="Date"
    )
    
    metadata_pretty = fields.Text(
        string="Metadata",
        compute='_pretty_xml_data'
    )
    
    folio = fields.Char(
        # string="Folio"
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
            # ('I', 'Ingreso'),
            ('I', 'Income (Ingreso)'),
            # ('E', 'Egreso'),
            ('E', 'Discharged (Egreso)'),
            # ('T', 'Traslado'),
            ('T', 'Transfer (Traslado)'),
            # ('P', 'Pago'),
            ('P', 'Payment (Pago)'),
            # ('N', 'Nomina')
            ('N', 'Payroll (Nómina)')
        ],
        # string="Tipo de documento",
        string="Document type",
        default="I"
    )
    
    xml_path = fields.Char(
        compute='_get_full_path'
    )
    
    get_cfdi_state = fields.Boolean(
        # string="¿Obtener estado de CFDI?",
        string="¿Get CFDI state?",
        default=False
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
                # 'name':'Asientos contables',
                'name':'Journal entries',
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
        
    def create_bill_showing_new_record(self):
        new_moves = self.env['account.move']
        for rec in self:
            new_moves += rec.create_bill()
        
        # # raise ValidationError(len(new_moves))
        if len(new_moves) == 1:
            return {
                # 'name':'Asientos contables',
                'name':'Journal entries',
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
                # 'name': 'Asientos Contables',
                'name': 'Journal entries',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': self.env.ref('account.view_in_invoice_tree').id,
                'res_model': 'account.move',
                'views': [(False, 'tree'),(False, 'form')],
                'context': "{'edit':1}",
                'domain': [('id','in',new_moves.ids)],
                'target': 'current',
            }
        
    def create_bill(self):
        #Check if UUID is already linked
        partner_bills = self.env['account.move'].search([('cfdi_document.uuid','=',self.uuid)])
        if len(partner_bills) > 0:
            # raise ValidationError("El UUID del documento que seleccionó ya se encuentra relacionado. Se recomienda revisar el listado de los documentos vinculados relacionados a el RFC ''" + str(self.rfc_emisor) + "'' para continuar...")
            raise ValidationError("The UUID of the document you selected is already linked. It is recommended to review the list of linked documents related to the RFC ''" + str(self.rfc_emisor) + "'' to continue...")
        
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
                
#             partner = self.env['res.partner'].search([('vat','=',data['rfc_emisor']),('is_company','=',True)])
            if len(partner) < 1:
                try:
                    partner = self.env['res.partner'].create({
                        'name': data['emisor'],
                        'vat': data['rfc_emisor']
                    })
                except:
                    pass
            payment_term = self.env['account.payment.term'].with_context(lang='es_MX').search([('name', '=', data['metodo_pago'])])
            if len(payment_term) == 0:
                if partner.property_supplier_payment_term_id.id:
                    payment_term = partner.property_supplier_payment_term_id

            currency_id = self.env['res.currency'].search([('name','=',data['moneda'])], limit=1)
            if len(currency_id) == 0:
                currency_id = self.env.company.currency_id
                    
            account_move = self.env['account.move'].create({
                'partner_id': partner.id,
                'invoice_date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'date': datetime.datetime.strptime(data['date'][0],'%Y-%m-%d'),
                'state': 'draft',
                'move_type': 'in_invoice' if data['type'] == 'I' else 'in_refund',
                'extract_state': 'no_extract_requested',
                'journal_id': self.env.company.sat_account_incoming_journal_id.id if data['type'] == 'I' else self.env.company.sat_account_egress_journal_id.id,
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
                                # raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
                                raise UserError("No registered taxes were found with a base of " + "{:.4f}".format(imp) + "%. Create it to continue...")
                            tax_list += result
                        tax_list_zero = self.env['account.tax'].search([('amount','=',0),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                        if len(tax_list_zero) == 0:
                            # raise UserError("No se encontraron impuestos registrados con base al 0.00%. Configurelo para continuar...")
                            raise UserError("No taxes registered with a base of 0.00% were found. Create it to continue...")

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
                                # raise UserError("No se encontraron retenciones registradas con base al " + "{:.4f}".format(ret) + "%. Configurela para continuar...")
                                raise UserError("No registered retentions were found with a base of " + "{:.4f}".format(ret) + "%. Create it to continue...")
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
                            # name += "Tasa "+str(float(traslado.getAttribute('TasaOCuota'))*100)+", "
                            name += "Rate "+str(float(traslado.getAttribute('TasaOCuota'))*100)+", "
    #                     if float(base) != importe and concepto.getAttribute('Unidad') == 'Litro':
                        if round(float(base),2) != round(float(importe),2):
                            is_gasoline = True
                    for retencion in retenciones:
                        if traslado.getAttribute('TipoFactor') == 'Tasa':
                            rets.append(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))
                            # name += "Retención "+str(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))+", "
                            name += "Retention "+str(round(-float(retencion.getAttribute('TasaOCuota'))*100,4))+", "
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
                                # raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
                                raise UserError("No registered taxes were found with a base of " + "{:.4f}".format(imp) + "%. Create it to continue...")
                            tax_list += result
                        tax_list_zero = self.env['account.tax'].search([('amount','=',0),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                        if len(tax_list_zero) == 0:
                            # raise UserError("No se encontraron impuestos registrados con base al 0.00%. Configurelo para continuar...")
                            raise UserError("No taxes registered with a base of 0.00% were found. Create it to continue...")

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
                            # 'name': line['description'] + " Tasa 0%",
                            'name': line['description'] + " Rate 0%",
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
                                # raise UserError("No se encontraron retenciones registradas con base al " + "{:.4f}".format(ret) + "%. Configurela para continuar...")
                                raise UserError("No registered retentions were found with a base of " + "{:.4f}".format(ret) + "%. Create it to continue...")
                            tax_rets += result
                        for imp in line['tasas']:
                            result = self.env['account.tax'].search([('amount','=',imp),('type_tax_use','=','purchase'),('cash_basis_transition_account_id.company_id.id','=',self.env.company.id),('active','=',True)], limit=1)
                            if len(result) == 0:
                                # raise UserError("No se encontraron impuestos registrados con base al " + "{:.4f}".format(imp) + "%. Configurelo para continuar...")
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
                        })
                        move_lines_list += move_line
                

            account_move.with_context(check_move_validity=False).write({
                'invoice_line_ids':move_lines_list.ids,
            })
                
            diferencia = data['total']-account_move.amount_total
            if  diferencia == 0:
                account_move.message_post(
                    # body='FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b>'.format(
                    #     data['uuid'],
                    #     data['total'],
                    #     '{:20,.2f}'.format(account_move.amount_total)
                    # )
                    body='INVOICE created from CFDI <b>[{}]</b>. \nTotal on CFDI: <b>{}</b> \nTotal on INVOICE: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total)
                    )
                )
            else:
                account_move.message_post(
                    # body = 'FACTURA creada a partir de CFDI <b>[{}]</b>. \nTotal CFDI: <b>{}</b> \nTotal FACTURA: <b>{}</b> \nDiferencia: <b>{}</b>'.format(
                    #     data['uuid'],
                    #     data['total'],
                    #     '{:20,.2f}'.format(account_move.amount_total),
                    #     '{:20,.2f}'.format(abs(diferencia))
                    # )
                    body = 'INVOICE created from CFDI <b>[{}]</b>. \nTotal on CFDI: <b>{}</b> \nTotal on INVOICE: <b>{}</b> \nDifference: <b>{}</b>'.format(
                        data['uuid'],
                        data['total'],
                        '{:20,.2f}'.format(account_move.amount_total),
                        '{:20,.2f}'.format(abs(diferencia))
                    )
                )
            return account_move
        else:
            # raise UserError("El RFC receptor del documento XML no coincide con el RFC de la empresa")
            raise UserError("The receptor RFC on XML document does not match with company RFC")
            
            
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