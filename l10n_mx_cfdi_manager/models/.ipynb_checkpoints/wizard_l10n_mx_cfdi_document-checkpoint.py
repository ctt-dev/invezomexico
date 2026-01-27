# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError , UserError

class WizardMoveDocument(models.TransientModel):
    _name = 'l10n_mx.cfdi_document_wizard'
    # _description = 'Wizard para vincular documento cfdi a moves'
    _description = 'Wizard for document vinculation'
    
    move_id = fields.Integer(
        # string="Factura"
        string="Invoice"
    )
    move_id_type = fields.Char(
        # string="Tipo de factura"
        string="Invoice type"
    )
    @api.depends('move_id_type')
    def compute_tipo_comprobante(self):
        for rec in self:
            tipo_comprobante = False
            if rec.move_id_type == "in_invoice":
                tipo_comprobante = "I"
            elif rec.move_id_type == "in_refund":
                tipo_comprobante = "E"
            rec.tipo_comprobante = tipo_comprobante    
    tipo_comprobante = fields.Char(
        # string="Tipo de factura",
        string="Type",
        compute=compute_tipo_comprobante,
        store=True
    )
    date = fields.Date(
        # string="Fecha"
        string="Date"
    )
    cfdi_document=fields.Many2one(
        'l10n_mx.cfdi_document',
        # string="Documento cfdi"
        string="CFDI document"
    )
    total=fields.Float(
        string="Total",
        related='cfdi_document.total'
    )
    cfdi_state=fields.Char(
        # string="Estado CFDI",
        string="CFDI state",
        related='cfdi_document.cfdi_state'
    )
    emisor=fields.Char(
        # string="Emisor",
        string="Emiter",
        related='cfdi_document.emisor'
    )
    folio = fields.Char(
        # string="Folio",
        string="Folio",
        related='cfdi_document.folio'
    )
    metadata=fields.Text(
        string="Metadata",
        related='cfdi_document.metadata_pretty'
    )
    
    partner_id_vat = fields.Char(
        string="RFC"
    )
    
    def event_wizard(self):
        if self.cfdi_document:
            partner_bills = self.env['account.move'].search([('cfdi_document.uuid','=',self.cfdi_document.uuid)])
            if len(partner_bills) > 0:
                # raise ValidationError("El UUID del documento que seleccionó ya se encuentra relacionado. Se recomienda revisar el listado de los documentos vinculados relacionados a el RFC ''" + str(self.cfdi_document.rfc_emisor) + "'' para continuar...")
                raise ValidationError("The UUID of the document you selected is already linked. It is recommended to review the list of linked documents related to the RFC ''" + str(self.cfdi_document.rfc_emisor) + "'' to continue...")
                
            move = self.env['account.move'].search([('id','=',self.move_id)])
            if self.cfdi_document.rfc_emisor != move.partner_id.vat:
                # raise UserError("RFC de documento CFDI no corresponde al del proveedor")
                raise UserError("RFC of CFDI document does not correspond to the supplier's RFC")
                
            if self.cfdi_document.total != move.amount_total:
                if round(abs(self.cfdi_document.total - move.amount_total),2) > self.env.company.dif_allowed:
                    # raise UserError("La diferencia entre el total del asiento contable y el CFDI relacionado es mayor a $" + "{:.2f}".format(self.env.company.dif_allowed) + " pesos.")
                    raise UserError("The difference between the total of the accounting entry and the related CFDI is greater than $" + "{:.2f}".format(self.env.company.dif_allowed) + " pesos.")
            
            move.write({
                'cfdi_document':self.cfdi_document.id
            })
            
            self.cfdi_document.write({
                'link_state':'link'
            })
        else:
            # raise UserError("Seleccione un documento")
            raise UserError("Select a document")
            
    @api.onchange('date')
    def onchange_date(self):
        self.cfdi_document = False